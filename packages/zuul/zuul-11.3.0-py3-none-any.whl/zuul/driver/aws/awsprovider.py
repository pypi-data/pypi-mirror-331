# Copyright 2022-2024 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import math

import zuul.provider.schema as provider_schema
from zuul.lib.voluputil import (
    Required, Optional, Nullable, discriminate, assemble, RequiredExclusive,
)

import voluptuous as vs

from zuul.driver.aws.awsendpoint import (
    AwsCreateStateMachine,
    AwsDeleteStateMachine,
)
from zuul.driver.aws.const import (
    SPOT,
    ON_DEMAND,
    VOLUME_QUOTA_CODES,
)
from zuul.model import QuotaInformation
from zuul.provider import (
    BaseProvider,
    BaseProviderFlavor,
    BaseProviderImage,
    BaseProviderLabel,
    BaseProviderSchema,
)


class AwsProviderImage(BaseProviderImage):
    aws_image_filters = {
        'name': str,
        'values': [str],
    }
    # This is used here and in flavors and labels
    inheritable_aws_volume_schema = vs.Schema({
        Optional('volume-size'): Nullable(int),
        Optional('volume-type', default='gp3'): str,
        Optional('iops'): Nullable(int),
        Optional('throughput'): Nullable(int),
    })
    aws_cloud_schema = vs.Schema({
        vs.Exclusive(Required('image-id'), 'spec'): str,
        vs.Exclusive(Required('image-filters'), 'spec'): [aws_image_filters],
        Required('type'): 'cloud',
    })
    cloud_schema = vs.All(
        assemble(
            BaseProviderImage.schema,
            aws_cloud_schema,
            inheritable_aws_volume_schema,
        ),
        RequiredExclusive('image_id', 'image_filters',
                          msg=('Provide either '
                               '"image-filters", or "image-id" keys'))
    )
    inheritable_aws_zuul_schema = vs.Schema({
        Optional('import-method', default='snapshot'): vs.Any(
            'snapshot', 'image', 'ebs-direct'),
        # None is an acceptable explicit value for imds-support
        Optional('imds-support', default=None): vs.Any('v2.0', None),
        Optional('architecture', default='x86_64'): str,
        Optional('ena-support', default=True): bool,
    })
    aws_zuul_schema = vs.Schema({
        Required('type'): 'zuul',
        Optional('tags', default=dict): {str: str},
    })
    zuul_schema = assemble(
        BaseProviderImage.schema,
        aws_zuul_schema,
        inheritable_aws_volume_schema,
        inheritable_aws_zuul_schema,
    )
    inheritable_schema = assemble(
        BaseProviderImage.inheritable_schema,
        inheritable_aws_volume_schema,
        inheritable_aws_zuul_schema,
    )
    schema = vs.Union(
        cloud_schema, zuul_schema,
        discriminant=discriminate(
            lambda val, alt: val['type'] == alt['type']))

    def __init__(self, image_config, provider_config):
        self.image_id = None
        self.image_filters = None
        super().__init__(image_config, provider_config)
        # Implement provider defaults
        if self.connection_type is None:
            self.connection_type = 'ssh'
        if self.connection_port is None:
            self.connection_port = 22


class AwsProviderFlavor(BaseProviderFlavor):
    aws_flavor_schema = vs.Schema({
        Required('instance-type'): str,
        Optional('dedicated-host', default=False): bool,
        Optional('ebs-optimized', default=False): bool,
        Optional('market-type', default='on-demand'): vs.Any(
            'on-demand', 'spot'),
    })

    inheritable_schema = assemble(
        BaseProviderFlavor.inheritable_schema,
        # This is already included via the image, but listed again
        # here for clarity.
        AwsProviderImage.inheritable_aws_volume_schema,
        provider_schema.cloud_flavor,
    )
    schema = assemble(
        BaseProviderFlavor.schema,
        provider_schema.cloud_flavor,
        AwsProviderImage.inheritable_aws_volume_schema,
        aws_flavor_schema,
    )


class AwsProviderLabel(BaseProviderLabel):
    inheritable_schema = assemble(
        BaseProviderLabel.inheritable_schema,
        # This is already included via the image, but listed again
        # here for clarity.
        AwsProviderImage.inheritable_aws_volume_schema,
        provider_schema.ssh_label,
    )
    schema = assemble(
        BaseProviderLabel.schema,
        AwsProviderImage.inheritable_aws_volume_schema,
        provider_schema.ssh_label,
    )

    image_flavor_inheritable_schema = assemble(
        AwsProviderImage.inheritable_aws_volume_schema,
    )


class AwsProviderSchema(BaseProviderSchema):
    def getLabelSchema(self):
        return AwsProviderLabel.schema

    def getImageSchema(self):
        return AwsProviderImage.schema

    def getFlavorSchema(self):
        return AwsProviderFlavor.schema

    def getProviderSchema(self):
        schema = super().getProviderSchema()
        object_storage = {
            vs.Required('bucket-name'): str,
        }

        aws_provider_schema = vs.Schema({
            Required('region'): str,
            Optional('object-storage'): Nullable(object_storage),
        })
        return assemble(
            schema,
            aws_provider_schema,
            AwsProviderImage.inheritable_schema,
            AwsProviderFlavor.inheritable_schema,
            AwsProviderLabel.inheritable_schema,
        )


class AwsProvider(BaseProvider, subclass_id='aws'):
    log = logging.getLogger("zuul.AwsProvider")
    schema = AwsProviderSchema().getProviderSchema()

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        # In listResources, we reconcile AMIs which appear to be
        # imports but have no nodepool tags, however it's possible
        # that these aren't nodepool images.  If we determine that's
        # the case, we'll add their ids here so we don't waste our
        # time on that again.  We do not need to serialize these;
        # these are ephemeral caches.
        self._set(
            not_our_images=set(),
            not_our_snapshots=set(),
        )

    @property
    def endpoint(self):
        ep = getattr(self, '_endpoint', None)
        if ep:
            return ep
        self._set(_endpoint=self.getEndpoint())
        return self._endpoint

    def parseImage(self, image_config, provider_config, connection):
        return AwsProviderImage(image_config, provider_config)

    def parseFlavor(self, flavor_config, provider_config, connection):
        return AwsProviderFlavor(flavor_config, provider_config)

    def parseLabel(self, label_config, provider_config, connection):
        return AwsProviderLabel(label_config, provider_config)

    def getEndpoint(self):
        return self.driver.getEndpoint(self)

    def getCreateStateMachine(self, node, image_external_id, log):
        # TODO: decide on a method of producing a hostname
        # that is max 15 chars.
        hostname = f"np{node.uuid[:13]}"
        label = self.labels[node.label]
        flavor = self.flavors[label.flavor]
        image = self.images[label.image]
        return AwsCreateStateMachine(
            self.endpoint,
            node,
            hostname,
            label,
            flavor,
            image,
            image_external_id,
            node.tags,
            log)

    def getDeleteStateMachine(self, node, log):
        return AwsDeleteStateMachine(self.endpoint, node, log)

    def listInstances(self):
        return self.endpoint.listInstances()

    def listResources(self):
        bucket_name = self.object_storage.get('bucket-name')

        self.endpoint._tagSnapshots(
            self.tenant_scoped_name, self.not_our_snapshots)
        self.endpoint._tagAmis(
            self.tenant_scoped_name, self.not_our_images)
        return self.endpoint.listResources(bucket_name)

    def deleteResource(self, resource):
        bucket_name = self.object_storage.get('bucket-name')
        self.endpoint.deleteResource(resource, bucket_name)

    def getQuotaLimits(self):
        # Get the instance and volume types that this provider handles
        instance_types = {}
        host_types = set()
        volume_types = set()
        ec2_quotas = self.endpoint._listEC2Quotas()
        ebs_quotas = self.endpoint._listEBSQuotas()
        for flavor in self.flavors.values():
            if flavor.dedicated_host:
                host_types.add(flavor.instance_type)
            else:
                if flavor.instance_type not in instance_types:
                    instance_types[flavor.instance_type] = set()
                instance_types[flavor.instance_type].add(
                    SPOT if flavor.market_type == 'spot' else ON_DEMAND)
            if flavor.volume_type:
                volume_types.add(flavor.volume_type)
        args = dict(default=math.inf)
        for instance_type in instance_types:
            for market_type_option in instance_types[instance_type]:
                code = self.endpoint._getQuotaCodeForInstanceType(
                    instance_type, market_type_option)
                if code in args:
                    continue
                if not code:
                    continue
                if code not in ec2_quotas:
                    self.log.warning(
                        "AWS quota code %s for instance type: %s not known",
                        code, instance_type)
                    continue
                args[code] = ec2_quotas[code]
        for host_type in host_types:
            code = self.endpoint._getQuotaCodeForHostType(host_type)
            if code in args:
                continue
            if not code:
                continue
            if code not in ec2_quotas:
                self.log.warning(
                    "AWS quota code %s for host type: %s not known",
                    code, host_type)
                continue
            args[code] = ec2_quotas[code]
        for volume_type in volume_types:
            vquota_codes = VOLUME_QUOTA_CODES.get(volume_type)
            if not vquota_codes:
                self.log.warning(
                    "Unknown quota code for volume type: %s",
                    volume_type)
                continue
            for resource, code in vquota_codes.items():
                if code in args:
                    continue
                if code not in ebs_quotas:
                    self.log.warning(
                        "AWS quota code %s for volume type: %s not known",
                        code, volume_type)
                    continue
                value = ebs_quotas[code]
                # Unit mismatch: storage limit is in TB, but usage
                # is in GB.  Translate the limit to GB.
                if resource == 'storage':
                    value *= 1000
                args[code] = value
        return QuotaInformation(**args)

    def getQuotaForLabel(self, label):
        flavor = self.flavors[label.flavor]
        return self.endpoint.getQuotaForLabel(label, flavor)

    def uploadImage(self, provider_image, image_name,
                    filename, image_format, metadata, md5, sha256):
        # TODO this needs to move to the section or connection config
        # since it's used by endpoints.
        bucket_name = self.object_storage.get('bucket-name')
        # TODO make this configurable
        # timeout = self.image_import_timeout
        timeout = 300
        return self.endpoint.uploadImage(
            provider_image, image_name,
            filename, image_format, metadata, md5, sha256,
            bucket_name, timeout)

    def deleteImage(self, external_id):
        self.endpoint.deleteImage(external_id)
