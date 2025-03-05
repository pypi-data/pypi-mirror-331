# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from Tea.model import TeaModel
from typing import Dict, List


class AddIpamPoolCidrRequest(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        client_token: str = None,
        dry_run: bool = None,
        ipam_pool_id: str = None,
        region_id: str = None,
    ):
        # This parameter is required.
        self.cidr = cidr
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_pool_id = ipam_pool_id
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class AddIpamPoolCidrResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class AddIpamPoolCidrResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: AddIpamPoolCidrResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = AddIpamPoolCidrResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class AssociateIpamResourceDiscoveryRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_id: str = None,
        ipam_resource_discovery_id: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_id = ipam_id
        # This parameter is required.
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class AssociateIpamResourceDiscoveryResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class AssociateIpamResourceDiscoveryResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: AssociateIpamResourceDiscoveryResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = AssociateIpamResourceDiscoveryResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ChangeResourceGroupRequest(TeaModel):
    def __init__(
        self,
        new_resource_group_id: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        resource_type: str = None,
    ):
        # This parameter is required.
        self.new_resource_group_id = new_resource_group_id
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        # This parameter is required.
        self.resource_id = resource_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        # This parameter is required.
        self.resource_type = resource_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.new_resource_group_id is not None:
            result['NewResourceGroupId'] = self.new_resource_group_id
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('NewResourceGroupId') is not None:
            self.new_resource_group_id = m.get('NewResourceGroupId')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        return self


class ChangeResourceGroupResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class ChangeResourceGroupResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ChangeResourceGroupResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ChangeResourceGroupResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateIpamRequestTag(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class CreateIpamRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_description: str = None,
        ipam_name: str = None,
        operating_region_list: List[str] = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_group_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        tag: List[CreateIpamRequestTag] = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        self.ipam_description = ipam_description
        self.ipam_name = ipam_name
        # This parameter is required.
        self.operating_region_list = operating_region_list
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        self.tag = tag

    def validate(self):
        if self.tag:
            for k in self.tag:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_description is not None:
            result['IpamDescription'] = self.ipam_description
        if self.ipam_name is not None:
            result['IpamName'] = self.ipam_name
        if self.operating_region_list is not None:
            result['OperatingRegionList'] = self.operating_region_list
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        result['Tag'] = []
        if self.tag is not None:
            for k in self.tag:
                result['Tag'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamDescription') is not None:
            self.ipam_description = m.get('IpamDescription')
        if m.get('IpamName') is not None:
            self.ipam_name = m.get('IpamName')
        if m.get('OperatingRegionList') is not None:
            self.operating_region_list = m.get('OperatingRegionList')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        self.tag = []
        if m.get('Tag') is not None:
            for k in m.get('Tag'):
                temp_model = CreateIpamRequestTag()
                self.tag.append(temp_model.from_map(k))
        return self


class CreateIpamResponseBody(TeaModel):
    def __init__(
        self,
        default_resource_discovery_association_id: str = None,
        default_resource_discovery_id: str = None,
        ipam_id: str = None,
        private_default_scope_id: str = None,
        public_default_scope_id: str = None,
        request_id: str = None,
        resource_discovery_association_count: int = None,
    ):
        self.default_resource_discovery_association_id = default_resource_discovery_association_id
        self.default_resource_discovery_id = default_resource_discovery_id
        self.ipam_id = ipam_id
        self.private_default_scope_id = private_default_scope_id
        self.public_default_scope_id = public_default_scope_id
        self.request_id = request_id
        self.resource_discovery_association_count = resource_discovery_association_count

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.default_resource_discovery_association_id is not None:
            result['DefaultResourceDiscoveryAssociationId'] = self.default_resource_discovery_association_id
        if self.default_resource_discovery_id is not None:
            result['DefaultResourceDiscoveryId'] = self.default_resource_discovery_id
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.private_default_scope_id is not None:
            result['PrivateDefaultScopeId'] = self.private_default_scope_id
        if self.public_default_scope_id is not None:
            result['PublicDefaultScopeId'] = self.public_default_scope_id
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.resource_discovery_association_count is not None:
            result['ResourceDiscoveryAssociationCount'] = self.resource_discovery_association_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('DefaultResourceDiscoveryAssociationId') is not None:
            self.default_resource_discovery_association_id = m.get('DefaultResourceDiscoveryAssociationId')
        if m.get('DefaultResourceDiscoveryId') is not None:
            self.default_resource_discovery_id = m.get('DefaultResourceDiscoveryId')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('PrivateDefaultScopeId') is not None:
            self.private_default_scope_id = m.get('PrivateDefaultScopeId')
        if m.get('PublicDefaultScopeId') is not None:
            self.public_default_scope_id = m.get('PublicDefaultScopeId')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('ResourceDiscoveryAssociationCount') is not None:
            self.resource_discovery_association_count = m.get('ResourceDiscoveryAssociationCount')
        return self


class CreateIpamResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateIpamResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateIpamResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateIpamPoolRequestTag(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class CreateIpamPoolRequest(TeaModel):
    def __init__(
        self,
        allocation_default_cidr_mask: int = None,
        allocation_max_cidr_mask: int = None,
        allocation_min_cidr_mask: int = None,
        auto_import: bool = None,
        client_token: str = None,
        dry_run: bool = None,
        ip_version: str = None,
        ipam_pool_description: str = None,
        ipam_pool_name: str = None,
        ipam_scope_id: str = None,
        owner_account: str = None,
        owner_id: int = None,
        pool_region_id: str = None,
        region_id: str = None,
        resource_group_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        source_ipam_pool_id: str = None,
        tag: List[CreateIpamPoolRequestTag] = None,
    ):
        self.allocation_default_cidr_mask = allocation_default_cidr_mask
        self.allocation_max_cidr_mask = allocation_max_cidr_mask
        self.allocation_min_cidr_mask = allocation_min_cidr_mask
        self.auto_import = auto_import
        self.client_token = client_token
        self.dry_run = dry_run
        self.ip_version = ip_version
        self.ipam_pool_description = ipam_pool_description
        self.ipam_pool_name = ipam_pool_name
        # This parameter is required.
        self.ipam_scope_id = ipam_scope_id
        self.owner_account = owner_account
        self.owner_id = owner_id
        self.pool_region_id = pool_region_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        self.source_ipam_pool_id = source_ipam_pool_id
        self.tag = tag

    def validate(self):
        if self.tag:
            for k in self.tag:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.allocation_default_cidr_mask is not None:
            result['AllocationDefaultCidrMask'] = self.allocation_default_cidr_mask
        if self.allocation_max_cidr_mask is not None:
            result['AllocationMaxCidrMask'] = self.allocation_max_cidr_mask
        if self.allocation_min_cidr_mask is not None:
            result['AllocationMinCidrMask'] = self.allocation_min_cidr_mask
        if self.auto_import is not None:
            result['AutoImport'] = self.auto_import
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ip_version is not None:
            result['IpVersion'] = self.ip_version
        if self.ipam_pool_description is not None:
            result['IpamPoolDescription'] = self.ipam_pool_description
        if self.ipam_pool_name is not None:
            result['IpamPoolName'] = self.ipam_pool_name
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.pool_region_id is not None:
            result['PoolRegionId'] = self.pool_region_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.source_ipam_pool_id is not None:
            result['SourceIpamPoolId'] = self.source_ipam_pool_id
        result['Tag'] = []
        if self.tag is not None:
            for k in self.tag:
                result['Tag'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AllocationDefaultCidrMask') is not None:
            self.allocation_default_cidr_mask = m.get('AllocationDefaultCidrMask')
        if m.get('AllocationMaxCidrMask') is not None:
            self.allocation_max_cidr_mask = m.get('AllocationMaxCidrMask')
        if m.get('AllocationMinCidrMask') is not None:
            self.allocation_min_cidr_mask = m.get('AllocationMinCidrMask')
        if m.get('AutoImport') is not None:
            self.auto_import = m.get('AutoImport')
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpVersion') is not None:
            self.ip_version = m.get('IpVersion')
        if m.get('IpamPoolDescription') is not None:
            self.ipam_pool_description = m.get('IpamPoolDescription')
        if m.get('IpamPoolName') is not None:
            self.ipam_pool_name = m.get('IpamPoolName')
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('PoolRegionId') is not None:
            self.pool_region_id = m.get('PoolRegionId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('SourceIpamPoolId') is not None:
            self.source_ipam_pool_id = m.get('SourceIpamPoolId')
        self.tag = []
        if m.get('Tag') is not None:
            for k in m.get('Tag'):
                temp_model = CreateIpamPoolRequestTag()
                self.tag.append(temp_model.from_map(k))
        return self


class CreateIpamPoolResponseBody(TeaModel):
    def __init__(
        self,
        ipam_pool_id: str = None,
        request_id: str = None,
    ):
        self.ipam_pool_id = ipam_pool_id
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class CreateIpamPoolResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateIpamPoolResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateIpamPoolResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateIpamPoolAllocationRequest(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        cidr_mask: int = None,
        client_token: str = None,
        dry_run: bool = None,
        ipam_pool_allocation_description: str = None,
        ipam_pool_allocation_name: str = None,
        ipam_pool_id: str = None,
        region_id: str = None,
    ):
        self.cidr = cidr
        self.cidr_mask = cidr_mask
        self.client_token = client_token
        self.dry_run = dry_run
        self.ipam_pool_allocation_description = ipam_pool_allocation_description
        self.ipam_pool_allocation_name = ipam_pool_allocation_name
        # This parameter is required.
        self.ipam_pool_id = ipam_pool_id
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.cidr_mask is not None:
            result['CidrMask'] = self.cidr_mask
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_pool_allocation_description is not None:
            result['IpamPoolAllocationDescription'] = self.ipam_pool_allocation_description
        if self.ipam_pool_allocation_name is not None:
            result['IpamPoolAllocationName'] = self.ipam_pool_allocation_name
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('CidrMask') is not None:
            self.cidr_mask = m.get('CidrMask')
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamPoolAllocationDescription') is not None:
            self.ipam_pool_allocation_description = m.get('IpamPoolAllocationDescription')
        if m.get('IpamPoolAllocationName') is not None:
            self.ipam_pool_allocation_name = m.get('IpamPoolAllocationName')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class CreateIpamPoolAllocationResponseBody(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        ipam_pool_allocation_id: str = None,
        request_id: str = None,
        source_cidr: str = None,
    ):
        self.cidr = cidr
        self.ipam_pool_allocation_id = ipam_pool_allocation_id
        self.request_id = request_id
        self.source_cidr = source_cidr

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.ipam_pool_allocation_id is not None:
            result['IpamPoolAllocationId'] = self.ipam_pool_allocation_id
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.source_cidr is not None:
            result['SourceCidr'] = self.source_cidr
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('IpamPoolAllocationId') is not None:
            self.ipam_pool_allocation_id = m.get('IpamPoolAllocationId')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('SourceCidr') is not None:
            self.source_cidr = m.get('SourceCidr')
        return self


class CreateIpamPoolAllocationResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateIpamPoolAllocationResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateIpamPoolAllocationResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateIpamResourceDiscoveryRequestTag(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class CreateIpamResourceDiscoveryRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_resource_discovery_description: str = None,
        ipam_resource_discovery_name: str = None,
        operating_region_list: List[str] = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_group_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        tag: List[CreateIpamResourceDiscoveryRequestTag] = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        self.ipam_resource_discovery_description = ipam_resource_discovery_description
        self.ipam_resource_discovery_name = ipam_resource_discovery_name
        # This parameter is required.
        self.operating_region_list = operating_region_list
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        self.tag = tag

    def validate(self):
        if self.tag:
            for k in self.tag:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_resource_discovery_description is not None:
            result['IpamResourceDiscoveryDescription'] = self.ipam_resource_discovery_description
        if self.ipam_resource_discovery_name is not None:
            result['IpamResourceDiscoveryName'] = self.ipam_resource_discovery_name
        if self.operating_region_list is not None:
            result['OperatingRegionList'] = self.operating_region_list
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        result['Tag'] = []
        if self.tag is not None:
            for k in self.tag:
                result['Tag'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamResourceDiscoveryDescription') is not None:
            self.ipam_resource_discovery_description = m.get('IpamResourceDiscoveryDescription')
        if m.get('IpamResourceDiscoveryName') is not None:
            self.ipam_resource_discovery_name = m.get('IpamResourceDiscoveryName')
        if m.get('OperatingRegionList') is not None:
            self.operating_region_list = m.get('OperatingRegionList')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        self.tag = []
        if m.get('Tag') is not None:
            for k in m.get('Tag'):
                temp_model = CreateIpamResourceDiscoveryRequestTag()
                self.tag.append(temp_model.from_map(k))
        return self


class CreateIpamResourceDiscoveryResponseBody(TeaModel):
    def __init__(
        self,
        ipam_resource_discovery_id: str = None,
        request_id: str = None,
    ):
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class CreateIpamResourceDiscoveryResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateIpamResourceDiscoveryResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateIpamResourceDiscoveryResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class CreateIpamScopeRequestTag(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class CreateIpamScopeRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_id: str = None,
        ipam_scope_description: str = None,
        ipam_scope_name: str = None,
        ipam_scope_type: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_group_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        tag: List[CreateIpamScopeRequestTag] = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_id = ipam_id
        self.ipam_scope_description = ipam_scope_description
        self.ipam_scope_name = ipam_scope_name
        self.ipam_scope_type = ipam_scope_type
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        self.tag = tag

    def validate(self):
        if self.tag:
            for k in self.tag:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_scope_description is not None:
            result['IpamScopeDescription'] = self.ipam_scope_description
        if self.ipam_scope_name is not None:
            result['IpamScopeName'] = self.ipam_scope_name
        if self.ipam_scope_type is not None:
            result['IpamScopeType'] = self.ipam_scope_type
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        result['Tag'] = []
        if self.tag is not None:
            for k in self.tag:
                result['Tag'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamScopeDescription') is not None:
            self.ipam_scope_description = m.get('IpamScopeDescription')
        if m.get('IpamScopeName') is not None:
            self.ipam_scope_name = m.get('IpamScopeName')
        if m.get('IpamScopeType') is not None:
            self.ipam_scope_type = m.get('IpamScopeType')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        self.tag = []
        if m.get('Tag') is not None:
            for k in m.get('Tag'):
                temp_model = CreateIpamScopeRequestTag()
                self.tag.append(temp_model.from_map(k))
        return self


class CreateIpamScopeResponseBody(TeaModel):
    def __init__(
        self,
        ipam_scope_id: str = None,
        request_id: str = None,
    ):
        self.ipam_scope_id = ipam_scope_id
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class CreateIpamScopeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: CreateIpamScopeResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = CreateIpamScopeResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteIpamRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_id: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_id = ipam_id
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class DeleteIpamResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class DeleteIpamResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteIpamResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteIpamResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteIpamPoolRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_pool_id: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_pool_id = ipam_pool_id
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class DeleteIpamPoolResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class DeleteIpamPoolResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteIpamPoolResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteIpamPoolResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteIpamPoolAllocationRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_pool_allocation_id: str = None,
        region_id: str = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_pool_allocation_id = ipam_pool_allocation_id
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_pool_allocation_id is not None:
            result['IpamPoolAllocationId'] = self.ipam_pool_allocation_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamPoolAllocationId') is not None:
            self.ipam_pool_allocation_id = m.get('IpamPoolAllocationId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class DeleteIpamPoolAllocationResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class DeleteIpamPoolAllocationResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteIpamPoolAllocationResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteIpamPoolAllocationResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteIpamPoolCidrRequest(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        client_token: str = None,
        dry_run: bool = None,
        ipam_pool_id: str = None,
        region_id: str = None,
    ):
        # This parameter is required.
        self.cidr = cidr
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_pool_id = ipam_pool_id
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class DeleteIpamPoolCidrResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class DeleteIpamPoolCidrResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteIpamPoolCidrResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteIpamPoolCidrResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteIpamResourceDiscoveryRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_resource_discovery_id: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class DeleteIpamResourceDiscoveryResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class DeleteIpamResourceDiscoveryResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteIpamResourceDiscoveryResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteIpamResourceDiscoveryResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DeleteIpamScopeRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_scope_id: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_scope_id = ipam_scope_id
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class DeleteIpamScopeResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class DeleteIpamScopeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DeleteIpamScopeResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DeleteIpamScopeResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class DissociateIpamResourceDiscoveryRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_id: str = None,
        ipam_resource_discovery_id: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        # This parameter is required.
        self.ipam_id = ipam_id
        # This parameter is required.
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class DissociateIpamResourceDiscoveryResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class DissociateIpamResourceDiscoveryResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: DissociateIpamResourceDiscoveryResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = DissociateIpamResourceDiscoveryResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetIpamPoolAllocationRequest(TeaModel):
    def __init__(
        self,
        ipam_pool_allocation_id: str = None,
        region_id: str = None,
    ):
        # This parameter is required.
        self.ipam_pool_allocation_id = ipam_pool_allocation_id
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_pool_allocation_id is not None:
            result['IpamPoolAllocationId'] = self.ipam_pool_allocation_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamPoolAllocationId') is not None:
            self.ipam_pool_allocation_id = m.get('IpamPoolAllocationId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class GetIpamPoolAllocationResponseBody(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        creation_time: str = None,
        ipam_pool_allocation_description: str = None,
        ipam_pool_allocation_id: str = None,
        ipam_pool_allocation_name: str = None,
        ipam_pool_id: str = None,
        region_id: str = None,
        request_id: str = None,
        resource_id: str = None,
        resource_owner_id: int = None,
        resource_region_id: str = None,
        resource_type: str = None,
        source_cidr: str = None,
        status: str = None,
    ):
        self.cidr = cidr
        self.creation_time = creation_time
        self.ipam_pool_allocation_description = ipam_pool_allocation_description
        self.ipam_pool_allocation_id = ipam_pool_allocation_id
        self.ipam_pool_allocation_name = ipam_pool_allocation_name
        self.ipam_pool_id = ipam_pool_id
        self.region_id = region_id
        self.request_id = request_id
        self.resource_id = resource_id
        self.resource_owner_id = resource_owner_id
        self.resource_region_id = resource_region_id
        self.resource_type = resource_type
        self.source_cidr = source_cidr
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.creation_time is not None:
            result['CreationTime'] = self.creation_time
        if self.ipam_pool_allocation_description is not None:
            result['IpamPoolAllocationDescription'] = self.ipam_pool_allocation_description
        if self.ipam_pool_allocation_id is not None:
            result['IpamPoolAllocationId'] = self.ipam_pool_allocation_id
        if self.ipam_pool_allocation_name is not None:
            result['IpamPoolAllocationName'] = self.ipam_pool_allocation_name
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_region_id is not None:
            result['ResourceRegionId'] = self.resource_region_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        if self.source_cidr is not None:
            result['SourceCidr'] = self.source_cidr
        if self.status is not None:
            result['Status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('CreationTime') is not None:
            self.creation_time = m.get('CreationTime')
        if m.get('IpamPoolAllocationDescription') is not None:
            self.ipam_pool_allocation_description = m.get('IpamPoolAllocationDescription')
        if m.get('IpamPoolAllocationId') is not None:
            self.ipam_pool_allocation_id = m.get('IpamPoolAllocationId')
        if m.get('IpamPoolAllocationName') is not None:
            self.ipam_pool_allocation_name = m.get('IpamPoolAllocationName')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceRegionId') is not None:
            self.resource_region_id = m.get('ResourceRegionId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        if m.get('SourceCidr') is not None:
            self.source_cidr = m.get('SourceCidr')
        if m.get('Status') is not None:
            self.status = m.get('Status')
        return self


class GetIpamPoolAllocationResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetIpamPoolAllocationResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetIpamPoolAllocationResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetIpamPoolNextAvailableCidrRequest(TeaModel):
    def __init__(
        self,
        cidr_block: str = None,
        cidr_mask: int = None,
        client_token: str = None,
        ipam_pool_id: str = None,
        region_id: str = None,
    ):
        self.cidr_block = cidr_block
        self.cidr_mask = cidr_mask
        self.client_token = client_token
        # This parameter is required.
        self.ipam_pool_id = ipam_pool_id
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr_block is not None:
            result['CidrBlock'] = self.cidr_block
        if self.cidr_mask is not None:
            result['CidrMask'] = self.cidr_mask
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CidrBlock') is not None:
            self.cidr_block = m.get('CidrBlock')
        if m.get('CidrMask') is not None:
            self.cidr_mask = m.get('CidrMask')
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class GetIpamPoolNextAvailableCidrResponseBody(TeaModel):
    def __init__(
        self,
        cidr_block: str = None,
        request_id: str = None,
    ):
        self.cidr_block = cidr_block
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr_block is not None:
            result['CidrBlock'] = self.cidr_block
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CidrBlock') is not None:
            self.cidr_block = m.get('CidrBlock')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class GetIpamPoolNextAvailableCidrResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetIpamPoolNextAvailableCidrResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetIpamPoolNextAvailableCidrResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class GetVpcIpamServiceStatusRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class GetVpcIpamServiceStatusResponseBody(TeaModel):
    def __init__(
        self,
        enabled: bool = None,
        request_id: str = None,
    ):
        self.enabled = enabled
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.enabled is not None:
            result['Enabled'] = self.enabled
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Enabled') is not None:
            self.enabled = m.get('Enabled')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class GetVpcIpamServiceStatusResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: GetVpcIpamServiceStatusResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = GetVpcIpamServiceStatusResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamDiscoveredResourceRequest(TeaModel):
    def __init__(
        self,
        ipam_resource_discovery_id: str = None,
        max_results: int = None,
        next_token: str = None,
        region_id: str = None,
        resource_region_id: str = None,
        resource_type: str = None,
    ):
        # This parameter is required.
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.max_results = max_results
        self.next_token = next_token
        # This parameter is required.
        self.region_id = region_id
        # This parameter is required.
        self.resource_region_id = resource_region_id
        self.resource_type = resource_type

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_region_id is not None:
            result['ResourceRegionId'] = self.resource_region_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceRegionId') is not None:
            self.resource_region_id = m.get('ResourceRegionId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        return self


class ListIpamDiscoveredResourceResponseBodyIpamDiscoveredResources(TeaModel):
    def __init__(
        self,
        ali_uid: int = None,
        cidr: str = None,
        discovery_time: str = None,
        ip_usage: str = None,
        ipam_resource_discovery_id: str = None,
        resource_id: str = None,
        resource_owner_id: int = None,
        resource_region_id: str = None,
        resource_type: str = None,
        source_cidr: str = None,
        vpc_id: str = None,
    ):
        self.ali_uid = ali_uid
        self.cidr = cidr
        self.discovery_time = discovery_time
        self.ip_usage = ip_usage
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.resource_id = resource_id
        self.resource_owner_id = resource_owner_id
        self.resource_region_id = resource_region_id
        self.resource_type = resource_type
        self.source_cidr = source_cidr
        self.vpc_id = vpc_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ali_uid is not None:
            result['AliUid'] = self.ali_uid
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.discovery_time is not None:
            result['DiscoveryTime'] = self.discovery_time
        if self.ip_usage is not None:
            result['IpUsage'] = self.ip_usage
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_region_id is not None:
            result['ResourceRegionId'] = self.resource_region_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        if self.source_cidr is not None:
            result['SourceCidr'] = self.source_cidr
        if self.vpc_id is not None:
            result['VpcId'] = self.vpc_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AliUid') is not None:
            self.ali_uid = m.get('AliUid')
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('DiscoveryTime') is not None:
            self.discovery_time = m.get('DiscoveryTime')
        if m.get('IpUsage') is not None:
            self.ip_usage = m.get('IpUsage')
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceRegionId') is not None:
            self.resource_region_id = m.get('ResourceRegionId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        if m.get('SourceCidr') is not None:
            self.source_cidr = m.get('SourceCidr')
        if m.get('VpcId') is not None:
            self.vpc_id = m.get('VpcId')
        return self


class ListIpamDiscoveredResourceResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipam_discovered_resources: List[ListIpamDiscoveredResourceResponseBodyIpamDiscoveredResources] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        self.ipam_discovered_resources = ipam_discovered_resources
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.total_count = total_count

    def validate(self):
        if self.ipam_discovered_resources:
            for k in self.ipam_discovered_resources:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['IpamDiscoveredResources'] = []
        if self.ipam_discovered_resources is not None:
            for k in self.ipam_discovered_resources:
                result['IpamDiscoveredResources'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipam_discovered_resources = []
        if m.get('IpamDiscoveredResources') is not None:
            for k in m.get('IpamDiscoveredResources'):
                temp_model = ListIpamDiscoveredResourceResponseBodyIpamDiscoveredResources()
                self.ipam_discovered_resources.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamDiscoveredResourceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamDiscoveredResourceResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamDiscoveredResourceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamPoolAllocationsRequest(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        ipam_pool_allocation_ids: List[str] = None,
        ipam_pool_allocation_name: str = None,
        ipam_pool_id: str = None,
        max_results: int = None,
        next_token: str = None,
        region_id: str = None,
    ):
        self.cidr = cidr
        self.ipam_pool_allocation_ids = ipam_pool_allocation_ids
        self.ipam_pool_allocation_name = ipam_pool_allocation_name
        # This parameter is required.
        self.ipam_pool_id = ipam_pool_id
        self.max_results = max_results
        self.next_token = next_token
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.ipam_pool_allocation_ids is not None:
            result['IpamPoolAllocationIds'] = self.ipam_pool_allocation_ids
        if self.ipam_pool_allocation_name is not None:
            result['IpamPoolAllocationName'] = self.ipam_pool_allocation_name
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('IpamPoolAllocationIds') is not None:
            self.ipam_pool_allocation_ids = m.get('IpamPoolAllocationIds')
        if m.get('IpamPoolAllocationName') is not None:
            self.ipam_pool_allocation_name = m.get('IpamPoolAllocationName')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class ListIpamPoolAllocationsResponseBodyIpamPoolAllocations(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        creation_time: str = None,
        ipam_pool_allocation_description: str = None,
        ipam_pool_allocation_id: str = None,
        ipam_pool_allocation_name: str = None,
        ipam_pool_id: str = None,
        region_id: str = None,
        resource_id: str = None,
        resource_owner_id: int = None,
        resource_region_id: str = None,
        resource_type: str = None,
        source_cidr: str = None,
        status: str = None,
    ):
        self.cidr = cidr
        self.creation_time = creation_time
        self.ipam_pool_allocation_description = ipam_pool_allocation_description
        self.ipam_pool_allocation_id = ipam_pool_allocation_id
        self.ipam_pool_allocation_name = ipam_pool_allocation_name
        self.ipam_pool_id = ipam_pool_id
        self.region_id = region_id
        self.resource_id = resource_id
        self.resource_owner_id = resource_owner_id
        self.resource_region_id = resource_region_id
        self.resource_type = resource_type
        self.source_cidr = source_cidr
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.creation_time is not None:
            result['CreationTime'] = self.creation_time
        if self.ipam_pool_allocation_description is not None:
            result['IpamPoolAllocationDescription'] = self.ipam_pool_allocation_description
        if self.ipam_pool_allocation_id is not None:
            result['IpamPoolAllocationId'] = self.ipam_pool_allocation_id
        if self.ipam_pool_allocation_name is not None:
            result['IpamPoolAllocationName'] = self.ipam_pool_allocation_name
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_region_id is not None:
            result['ResourceRegionId'] = self.resource_region_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        if self.source_cidr is not None:
            result['SourceCidr'] = self.source_cidr
        if self.status is not None:
            result['Status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('CreationTime') is not None:
            self.creation_time = m.get('CreationTime')
        if m.get('IpamPoolAllocationDescription') is not None:
            self.ipam_pool_allocation_description = m.get('IpamPoolAllocationDescription')
        if m.get('IpamPoolAllocationId') is not None:
            self.ipam_pool_allocation_id = m.get('IpamPoolAllocationId')
        if m.get('IpamPoolAllocationName') is not None:
            self.ipam_pool_allocation_name = m.get('IpamPoolAllocationName')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceRegionId') is not None:
            self.resource_region_id = m.get('ResourceRegionId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        if m.get('SourceCidr') is not None:
            self.source_cidr = m.get('SourceCidr')
        if m.get('Status') is not None:
            self.status = m.get('Status')
        return self


class ListIpamPoolAllocationsResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipam_pool_allocations: List[ListIpamPoolAllocationsResponseBodyIpamPoolAllocations] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        self.ipam_pool_allocations = ipam_pool_allocations
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.total_count = total_count

    def validate(self):
        if self.ipam_pool_allocations:
            for k in self.ipam_pool_allocations:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['IpamPoolAllocations'] = []
        if self.ipam_pool_allocations is not None:
            for k in self.ipam_pool_allocations:
                result['IpamPoolAllocations'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipam_pool_allocations = []
        if m.get('IpamPoolAllocations') is not None:
            for k in m.get('IpamPoolAllocations'):
                temp_model = ListIpamPoolAllocationsResponseBodyIpamPoolAllocations()
                self.ipam_pool_allocations.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamPoolAllocationsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamPoolAllocationsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamPoolAllocationsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamPoolCidrsRequest(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        ipam_pool_id: str = None,
        max_results: int = None,
        next_token: str = None,
        region_id: str = None,
    ):
        self.cidr = cidr
        # This parameter is required.
        self.ipam_pool_id = ipam_pool_id
        self.max_results = max_results
        self.next_token = next_token
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class ListIpamPoolCidrsResponseBodyIpamPoolCidrs(TeaModel):
    def __init__(
        self,
        cidr: str = None,
        ipam_pool_id: str = None,
        status: str = None,
    ):
        self.cidr = cidr
        self.ipam_pool_id = ipam_pool_id
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.status is not None:
            result['Status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('Status') is not None:
            self.status = m.get('Status')
        return self


class ListIpamPoolCidrsResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipam_pool_cidrs: List[ListIpamPoolCidrsResponseBodyIpamPoolCidrs] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        self.ipam_pool_cidrs = ipam_pool_cidrs
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.total_count = total_count

    def validate(self):
        if self.ipam_pool_cidrs:
            for k in self.ipam_pool_cidrs:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['IpamPoolCidrs'] = []
        if self.ipam_pool_cidrs is not None:
            for k in self.ipam_pool_cidrs:
                result['IpamPoolCidrs'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipam_pool_cidrs = []
        if m.get('IpamPoolCidrs') is not None:
            for k in m.get('IpamPoolCidrs'):
                temp_model = ListIpamPoolCidrsResponseBodyIpamPoolCidrs()
                self.ipam_pool_cidrs.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamPoolCidrsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamPoolCidrsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamPoolCidrsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamPoolsRequestTags(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListIpamPoolsRequest(TeaModel):
    def __init__(
        self,
        ipam_pool_ids: List[str] = None,
        ipam_pool_name: str = None,
        ipam_scope_id: str = None,
        is_shared: bool = None,
        max_results: int = None,
        next_token: str = None,
        owner_account: str = None,
        owner_id: int = None,
        pool_region_id: str = None,
        region_id: str = None,
        resource_group_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        source_ipam_pool_id: str = None,
        tags: List[ListIpamPoolsRequestTags] = None,
    ):
        self.ipam_pool_ids = ipam_pool_ids
        self.ipam_pool_name = ipam_pool_name
        self.ipam_scope_id = ipam_scope_id
        self.is_shared = is_shared
        self.max_results = max_results
        self.next_token = next_token
        self.owner_account = owner_account
        self.owner_id = owner_id
        self.pool_region_id = pool_region_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        self.source_ipam_pool_id = source_ipam_pool_id
        self.tags = tags

    def validate(self):
        if self.tags:
            for k in self.tags:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_pool_ids is not None:
            result['IpamPoolIds'] = self.ipam_pool_ids
        if self.ipam_pool_name is not None:
            result['IpamPoolName'] = self.ipam_pool_name
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.is_shared is not None:
            result['IsShared'] = self.is_shared
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.pool_region_id is not None:
            result['PoolRegionId'] = self.pool_region_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.source_ipam_pool_id is not None:
            result['SourceIpamPoolId'] = self.source_ipam_pool_id
        result['Tags'] = []
        if self.tags is not None:
            for k in self.tags:
                result['Tags'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamPoolIds') is not None:
            self.ipam_pool_ids = m.get('IpamPoolIds')
        if m.get('IpamPoolName') is not None:
            self.ipam_pool_name = m.get('IpamPoolName')
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('IsShared') is not None:
            self.is_shared = m.get('IsShared')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('PoolRegionId') is not None:
            self.pool_region_id = m.get('PoolRegionId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('SourceIpamPoolId') is not None:
            self.source_ipam_pool_id = m.get('SourceIpamPoolId')
        self.tags = []
        if m.get('Tags') is not None:
            for k in m.get('Tags'):
                temp_model = ListIpamPoolsRequestTags()
                self.tags.append(temp_model.from_map(k))
        return self


class ListIpamPoolsResponseBodyIpamPoolsTags(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListIpamPoolsResponseBodyIpamPools(TeaModel):
    def __init__(
        self,
        allocation_default_cidr_mask: int = None,
        allocation_max_cidr_mask: int = None,
        allocation_min_cidr_mask: int = None,
        auto_import: bool = None,
        create_time: str = None,
        has_sub_pool: bool = None,
        ip_version: str = None,
        ipam_id: str = None,
        ipam_pool_description: str = None,
        ipam_pool_id: str = None,
        ipam_pool_name: str = None,
        ipam_region_id: str = None,
        ipam_scope_id: str = None,
        ipam_scope_type: str = None,
        is_shared: bool = None,
        owner_id: int = None,
        pool_depth: int = None,
        pool_region_id: str = None,
        region_id: str = None,
        resource_group_id: str = None,
        source_ipam_pool_id: str = None,
        status: str = None,
        tags: List[ListIpamPoolsResponseBodyIpamPoolsTags] = None,
    ):
        self.allocation_default_cidr_mask = allocation_default_cidr_mask
        self.allocation_max_cidr_mask = allocation_max_cidr_mask
        self.allocation_min_cidr_mask = allocation_min_cidr_mask
        self.auto_import = auto_import
        self.create_time = create_time
        self.has_sub_pool = has_sub_pool
        self.ip_version = ip_version
        self.ipam_id = ipam_id
        self.ipam_pool_description = ipam_pool_description
        self.ipam_pool_id = ipam_pool_id
        self.ipam_pool_name = ipam_pool_name
        self.ipam_region_id = ipam_region_id
        self.ipam_scope_id = ipam_scope_id
        self.ipam_scope_type = ipam_scope_type
        self.is_shared = is_shared
        self.owner_id = owner_id
        self.pool_depth = pool_depth
        self.pool_region_id = pool_region_id
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.source_ipam_pool_id = source_ipam_pool_id
        self.status = status
        self.tags = tags

    def validate(self):
        if self.tags:
            for k in self.tags:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.allocation_default_cidr_mask is not None:
            result['AllocationDefaultCidrMask'] = self.allocation_default_cidr_mask
        if self.allocation_max_cidr_mask is not None:
            result['AllocationMaxCidrMask'] = self.allocation_max_cidr_mask
        if self.allocation_min_cidr_mask is not None:
            result['AllocationMinCidrMask'] = self.allocation_min_cidr_mask
        if self.auto_import is not None:
            result['AutoImport'] = self.auto_import
        if self.create_time is not None:
            result['CreateTime'] = self.create_time
        if self.has_sub_pool is not None:
            result['HasSubPool'] = self.has_sub_pool
        if self.ip_version is not None:
            result['IpVersion'] = self.ip_version
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_pool_description is not None:
            result['IpamPoolDescription'] = self.ipam_pool_description
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.ipam_pool_name is not None:
            result['IpamPoolName'] = self.ipam_pool_name
        if self.ipam_region_id is not None:
            result['IpamRegionId'] = self.ipam_region_id
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.ipam_scope_type is not None:
            result['IpamScopeType'] = self.ipam_scope_type
        if self.is_shared is not None:
            result['IsShared'] = self.is_shared
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.pool_depth is not None:
            result['PoolDepth'] = self.pool_depth
        if self.pool_region_id is not None:
            result['PoolRegionId'] = self.pool_region_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.source_ipam_pool_id is not None:
            result['SourceIpamPoolId'] = self.source_ipam_pool_id
        if self.status is not None:
            result['Status'] = self.status
        result['Tags'] = []
        if self.tags is not None:
            for k in self.tags:
                result['Tags'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AllocationDefaultCidrMask') is not None:
            self.allocation_default_cidr_mask = m.get('AllocationDefaultCidrMask')
        if m.get('AllocationMaxCidrMask') is not None:
            self.allocation_max_cidr_mask = m.get('AllocationMaxCidrMask')
        if m.get('AllocationMinCidrMask') is not None:
            self.allocation_min_cidr_mask = m.get('AllocationMinCidrMask')
        if m.get('AutoImport') is not None:
            self.auto_import = m.get('AutoImport')
        if m.get('CreateTime') is not None:
            self.create_time = m.get('CreateTime')
        if m.get('HasSubPool') is not None:
            self.has_sub_pool = m.get('HasSubPool')
        if m.get('IpVersion') is not None:
            self.ip_version = m.get('IpVersion')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamPoolDescription') is not None:
            self.ipam_pool_description = m.get('IpamPoolDescription')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('IpamPoolName') is not None:
            self.ipam_pool_name = m.get('IpamPoolName')
        if m.get('IpamRegionId') is not None:
            self.ipam_region_id = m.get('IpamRegionId')
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('IpamScopeType') is not None:
            self.ipam_scope_type = m.get('IpamScopeType')
        if m.get('IsShared') is not None:
            self.is_shared = m.get('IsShared')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('PoolDepth') is not None:
            self.pool_depth = m.get('PoolDepth')
        if m.get('PoolRegionId') is not None:
            self.pool_region_id = m.get('PoolRegionId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('SourceIpamPoolId') is not None:
            self.source_ipam_pool_id = m.get('SourceIpamPoolId')
        if m.get('Status') is not None:
            self.status = m.get('Status')
        self.tags = []
        if m.get('Tags') is not None:
            for k in m.get('Tags'):
                temp_model = ListIpamPoolsResponseBodyIpamPoolsTags()
                self.tags.append(temp_model.from_map(k))
        return self


class ListIpamPoolsResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipam_pools: List[ListIpamPoolsResponseBodyIpamPools] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        self.ipam_pools = ipam_pools
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.total_count = total_count

    def validate(self):
        if self.ipam_pools:
            for k in self.ipam_pools:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['IpamPools'] = []
        if self.ipam_pools is not None:
            for k in self.ipam_pools:
                result['IpamPools'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipam_pools = []
        if m.get('IpamPools') is not None:
            for k in m.get('IpamPools'):
                temp_model = ListIpamPoolsResponseBodyIpamPools()
                self.ipam_pools.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamPoolsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamPoolsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamPoolsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamResourceCidrsRequest(TeaModel):
    def __init__(
        self,
        ipam_pool_id: str = None,
        ipam_scope_id: str = None,
        max_results: int = None,
        next_token: str = None,
        region_id: str = None,
        resource_id: str = None,
        resource_owner_id: int = None,
        resource_type: str = None,
        vpc_id: str = None,
    ):
        self.ipam_pool_id = ipam_pool_id
        self.ipam_scope_id = ipam_scope_id
        self.max_results = max_results
        self.next_token = next_token
        # This parameter is required.
        self.region_id = region_id
        self.resource_id = resource_id
        self.resource_owner_id = resource_owner_id
        self.resource_type = resource_type
        self.vpc_id = vpc_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        if self.vpc_id is not None:
            result['VpcId'] = self.vpc_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        if m.get('VpcId') is not None:
            self.vpc_id = m.get('VpcId')
        return self


class ListIpamResourceCidrsResponseBodyIpamResourceCidrsOverlapDetail(TeaModel):
    def __init__(
        self,
        overlap_resource_cidr: str = None,
        overlap_resource_id: str = None,
        overlap_resource_region: str = None,
    ):
        self.overlap_resource_cidr = overlap_resource_cidr
        self.overlap_resource_id = overlap_resource_id
        self.overlap_resource_region = overlap_resource_region

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.overlap_resource_cidr is not None:
            result['OverlapResourceCidr'] = self.overlap_resource_cidr
        if self.overlap_resource_id is not None:
            result['OverlapResourceId'] = self.overlap_resource_id
        if self.overlap_resource_region is not None:
            result['OverlapResourceRegion'] = self.overlap_resource_region
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('OverlapResourceCidr') is not None:
            self.overlap_resource_cidr = m.get('OverlapResourceCidr')
        if m.get('OverlapResourceId') is not None:
            self.overlap_resource_id = m.get('OverlapResourceId')
        if m.get('OverlapResourceRegion') is not None:
            self.overlap_resource_region = m.get('OverlapResourceRegion')
        return self


class ListIpamResourceCidrsResponseBodyIpamResourceCidrs(TeaModel):
    def __init__(
        self,
        ali_uid: int = None,
        cidr: str = None,
        compliance_status: str = None,
        ip_usage: str = None,
        ipam_allocation_id: str = None,
        ipam_id: str = None,
        ipam_pool_id: str = None,
        ipam_scope_id: str = None,
        management_status: str = None,
        overlap_detail: List[ListIpamResourceCidrsResponseBodyIpamResourceCidrsOverlapDetail] = None,
        overlap_status: str = None,
        resource_id: str = None,
        resource_owner_id: int = None,
        resource_region_id: str = None,
        resource_type: str = None,
        source_cidr: str = None,
        status: str = None,
        vpc_id: str = None,
    ):
        self.ali_uid = ali_uid
        self.cidr = cidr
        self.compliance_status = compliance_status
        self.ip_usage = ip_usage
        self.ipam_allocation_id = ipam_allocation_id
        self.ipam_id = ipam_id
        self.ipam_pool_id = ipam_pool_id
        self.ipam_scope_id = ipam_scope_id
        self.management_status = management_status
        self.overlap_detail = overlap_detail
        self.overlap_status = overlap_status
        self.resource_id = resource_id
        self.resource_owner_id = resource_owner_id
        self.resource_region_id = resource_region_id
        self.resource_type = resource_type
        self.source_cidr = source_cidr
        self.status = status
        self.vpc_id = vpc_id

    def validate(self):
        if self.overlap_detail:
            for k in self.overlap_detail:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ali_uid is not None:
            result['AliUid'] = self.ali_uid
        if self.cidr is not None:
            result['Cidr'] = self.cidr
        if self.compliance_status is not None:
            result['ComplianceStatus'] = self.compliance_status
        if self.ip_usage is not None:
            result['IpUsage'] = self.ip_usage
        if self.ipam_allocation_id is not None:
            result['IpamAllocationId'] = self.ipam_allocation_id
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.management_status is not None:
            result['ManagementStatus'] = self.management_status
        result['OverlapDetail'] = []
        if self.overlap_detail is not None:
            for k in self.overlap_detail:
                result['OverlapDetail'].append(k.to_map() if k else None)
        if self.overlap_status is not None:
            result['OverlapStatus'] = self.overlap_status
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_region_id is not None:
            result['ResourceRegionId'] = self.resource_region_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        if self.source_cidr is not None:
            result['SourceCidr'] = self.source_cidr
        if self.status is not None:
            result['Status'] = self.status
        if self.vpc_id is not None:
            result['VpcId'] = self.vpc_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AliUid') is not None:
            self.ali_uid = m.get('AliUid')
        if m.get('Cidr') is not None:
            self.cidr = m.get('Cidr')
        if m.get('ComplianceStatus') is not None:
            self.compliance_status = m.get('ComplianceStatus')
        if m.get('IpUsage') is not None:
            self.ip_usage = m.get('IpUsage')
        if m.get('IpamAllocationId') is not None:
            self.ipam_allocation_id = m.get('IpamAllocationId')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('ManagementStatus') is not None:
            self.management_status = m.get('ManagementStatus')
        self.overlap_detail = []
        if m.get('OverlapDetail') is not None:
            for k in m.get('OverlapDetail'):
                temp_model = ListIpamResourceCidrsResponseBodyIpamResourceCidrsOverlapDetail()
                self.overlap_detail.append(temp_model.from_map(k))
        if m.get('OverlapStatus') is not None:
            self.overlap_status = m.get('OverlapStatus')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceRegionId') is not None:
            self.resource_region_id = m.get('ResourceRegionId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        if m.get('SourceCidr') is not None:
            self.source_cidr = m.get('SourceCidr')
        if m.get('Status') is not None:
            self.status = m.get('Status')
        if m.get('VpcId') is not None:
            self.vpc_id = m.get('VpcId')
        return self


class ListIpamResourceCidrsResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipam_resource_cidrs: List[ListIpamResourceCidrsResponseBodyIpamResourceCidrs] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        self.ipam_resource_cidrs = ipam_resource_cidrs
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.total_count = total_count

    def validate(self):
        if self.ipam_resource_cidrs:
            for k in self.ipam_resource_cidrs:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['IpamResourceCidrs'] = []
        if self.ipam_resource_cidrs is not None:
            for k in self.ipam_resource_cidrs:
                result['IpamResourceCidrs'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipam_resource_cidrs = []
        if m.get('IpamResourceCidrs') is not None:
            for k in m.get('IpamResourceCidrs'):
                temp_model = ListIpamResourceCidrsResponseBodyIpamResourceCidrs()
                self.ipam_resource_cidrs.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamResourceCidrsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamResourceCidrsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamResourceCidrsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamResourceDiscoveriesRequestTags(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListIpamResourceDiscoveriesRequest(TeaModel):
    def __init__(
        self,
        ipam_resource_discovery_ids: List[str] = None,
        ipam_resource_discovery_name: str = None,
        is_shared: bool = None,
        max_results: int = None,
        next_token: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_group_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        tags: List[ListIpamResourceDiscoveriesRequestTags] = None,
        type: str = None,
    ):
        self.ipam_resource_discovery_ids = ipam_resource_discovery_ids
        self.ipam_resource_discovery_name = ipam_resource_discovery_name
        self.is_shared = is_shared
        self.max_results = max_results
        self.next_token = next_token
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        self.tags = tags
        self.type = type

    def validate(self):
        if self.tags:
            for k in self.tags:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_resource_discovery_ids is not None:
            result['IpamResourceDiscoveryIds'] = self.ipam_resource_discovery_ids
        if self.ipam_resource_discovery_name is not None:
            result['IpamResourceDiscoveryName'] = self.ipam_resource_discovery_name
        if self.is_shared is not None:
            result['IsShared'] = self.is_shared
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        result['Tags'] = []
        if self.tags is not None:
            for k in self.tags:
                result['Tags'].append(k.to_map() if k else None)
        if self.type is not None:
            result['Type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamResourceDiscoveryIds') is not None:
            self.ipam_resource_discovery_ids = m.get('IpamResourceDiscoveryIds')
        if m.get('IpamResourceDiscoveryName') is not None:
            self.ipam_resource_discovery_name = m.get('IpamResourceDiscoveryName')
        if m.get('IsShared') is not None:
            self.is_shared = m.get('IsShared')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        self.tags = []
        if m.get('Tags') is not None:
            for k in m.get('Tags'):
                temp_model = ListIpamResourceDiscoveriesRequestTags()
                self.tags.append(temp_model.from_map(k))
        if m.get('Type') is not None:
            self.type = m.get('Type')
        return self


class ListIpamResourceDiscoveriesResponseBodyIpamResourceDiscoveriesTags(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListIpamResourceDiscoveriesResponseBodyIpamResourceDiscoveries(TeaModel):
    def __init__(
        self,
        create_time: str = None,
        ipam_resource_discovery_description: str = None,
        ipam_resource_discovery_id: str = None,
        ipam_resource_discovery_name: str = None,
        ipam_resource_discovery_status: str = None,
        operating_region_list: List[str] = None,
        owner_id: int = None,
        region_id: str = None,
        resource_group_id: str = None,
        share_type: str = None,
        tags: List[ListIpamResourceDiscoveriesResponseBodyIpamResourceDiscoveriesTags] = None,
        type: str = None,
    ):
        self.create_time = create_time
        self.ipam_resource_discovery_description = ipam_resource_discovery_description
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.ipam_resource_discovery_name = ipam_resource_discovery_name
        self.ipam_resource_discovery_status = ipam_resource_discovery_status
        self.operating_region_list = operating_region_list
        self.owner_id = owner_id
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.share_type = share_type
        self.tags = tags
        self.type = type

    def validate(self):
        if self.tags:
            for k in self.tags:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['CreateTime'] = self.create_time
        if self.ipam_resource_discovery_description is not None:
            result['IpamResourceDiscoveryDescription'] = self.ipam_resource_discovery_description
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.ipam_resource_discovery_name is not None:
            result['IpamResourceDiscoveryName'] = self.ipam_resource_discovery_name
        if self.ipam_resource_discovery_status is not None:
            result['IpamResourceDiscoveryStatus'] = self.ipam_resource_discovery_status
        if self.operating_region_list is not None:
            result['OperatingRegionList'] = self.operating_region_list
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.share_type is not None:
            result['ShareType'] = self.share_type
        result['Tags'] = []
        if self.tags is not None:
            for k in self.tags:
                result['Tags'].append(k.to_map() if k else None)
        if self.type is not None:
            result['Type'] = self.type
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CreateTime') is not None:
            self.create_time = m.get('CreateTime')
        if m.get('IpamResourceDiscoveryDescription') is not None:
            self.ipam_resource_discovery_description = m.get('IpamResourceDiscoveryDescription')
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('IpamResourceDiscoveryName') is not None:
            self.ipam_resource_discovery_name = m.get('IpamResourceDiscoveryName')
        if m.get('IpamResourceDiscoveryStatus') is not None:
            self.ipam_resource_discovery_status = m.get('IpamResourceDiscoveryStatus')
        if m.get('OperatingRegionList') is not None:
            self.operating_region_list = m.get('OperatingRegionList')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ShareType') is not None:
            self.share_type = m.get('ShareType')
        self.tags = []
        if m.get('Tags') is not None:
            for k in m.get('Tags'):
                temp_model = ListIpamResourceDiscoveriesResponseBodyIpamResourceDiscoveriesTags()
                self.tags.append(temp_model.from_map(k))
        if m.get('Type') is not None:
            self.type = m.get('Type')
        return self


class ListIpamResourceDiscoveriesResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipam_resource_discoveries: List[ListIpamResourceDiscoveriesResponseBodyIpamResourceDiscoveries] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        self.ipam_resource_discoveries = ipam_resource_discoveries
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.total_count = total_count

    def validate(self):
        if self.ipam_resource_discoveries:
            for k in self.ipam_resource_discoveries:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['IpamResourceDiscoveries'] = []
        if self.ipam_resource_discoveries is not None:
            for k in self.ipam_resource_discoveries:
                result['IpamResourceDiscoveries'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipam_resource_discoveries = []
        if m.get('IpamResourceDiscoveries') is not None:
            for k in m.get('IpamResourceDiscoveries'):
                temp_model = ListIpamResourceDiscoveriesResponseBodyIpamResourceDiscoveries()
                self.ipam_resource_discoveries.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamResourceDiscoveriesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamResourceDiscoveriesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamResourceDiscoveriesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamResourceDiscoveryAssociationsRequest(TeaModel):
    def __init__(
        self,
        ipam_id: str = None,
        ipam_resource_discovery_id: str = None,
        max_results: int = None,
        next_token: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.ipam_id = ipam_id
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.max_results = max_results
        self.next_token = next_token
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class ListIpamResourceDiscoveryAssociationsResponseBodyIpamResourceDiscoveryAssociations(TeaModel):
    def __init__(
        self,
        ipam_id: str = None,
        ipam_resource_discovery_id: str = None,
        ipam_resource_discovery_owner_id: str = None,
        ipam_resource_discovery_status: str = None,
        ipam_resource_discovery_type: str = None,
        status: str = None,
    ):
        self.ipam_id = ipam_id
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.ipam_resource_discovery_owner_id = ipam_resource_discovery_owner_id
        self.ipam_resource_discovery_status = ipam_resource_discovery_status
        self.ipam_resource_discovery_type = ipam_resource_discovery_type
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.ipam_resource_discovery_owner_id is not None:
            result['IpamResourceDiscoveryOwnerId'] = self.ipam_resource_discovery_owner_id
        if self.ipam_resource_discovery_status is not None:
            result['IpamResourceDiscoveryStatus'] = self.ipam_resource_discovery_status
        if self.ipam_resource_discovery_type is not None:
            result['IpamResourceDiscoveryType'] = self.ipam_resource_discovery_type
        if self.status is not None:
            result['Status'] = self.status
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('IpamResourceDiscoveryOwnerId') is not None:
            self.ipam_resource_discovery_owner_id = m.get('IpamResourceDiscoveryOwnerId')
        if m.get('IpamResourceDiscoveryStatus') is not None:
            self.ipam_resource_discovery_status = m.get('IpamResourceDiscoveryStatus')
        if m.get('IpamResourceDiscoveryType') is not None:
            self.ipam_resource_discovery_type = m.get('IpamResourceDiscoveryType')
        if m.get('Status') is not None:
            self.status = m.get('Status')
        return self


class ListIpamResourceDiscoveryAssociationsResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipam_resource_discovery_associations: List[ListIpamResourceDiscoveryAssociationsResponseBodyIpamResourceDiscoveryAssociations] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        self.ipam_resource_discovery_associations = ipam_resource_discovery_associations
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.total_count = total_count

    def validate(self):
        if self.ipam_resource_discovery_associations:
            for k in self.ipam_resource_discovery_associations:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['IpamResourceDiscoveryAssociations'] = []
        if self.ipam_resource_discovery_associations is not None:
            for k in self.ipam_resource_discovery_associations:
                result['IpamResourceDiscoveryAssociations'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipam_resource_discovery_associations = []
        if m.get('IpamResourceDiscoveryAssociations') is not None:
            for k in m.get('IpamResourceDiscoveryAssociations'):
                temp_model = ListIpamResourceDiscoveryAssociationsResponseBodyIpamResourceDiscoveryAssociations()
                self.ipam_resource_discovery_associations.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamResourceDiscoveryAssociationsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamResourceDiscoveryAssociationsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamResourceDiscoveryAssociationsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamScopesRequestTags(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListIpamScopesRequest(TeaModel):
    def __init__(
        self,
        ipam_id: str = None,
        ipam_scope_ids: List[str] = None,
        ipam_scope_name: str = None,
        ipam_scope_type: str = None,
        max_results: int = None,
        next_token: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_group_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        tags: List[ListIpamScopesRequestTags] = None,
    ):
        self.ipam_id = ipam_id
        self.ipam_scope_ids = ipam_scope_ids
        self.ipam_scope_name = ipam_scope_name
        self.ipam_scope_type = ipam_scope_type
        self.max_results = max_results
        self.next_token = next_token
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        self.tags = tags

    def validate(self):
        if self.tags:
            for k in self.tags:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_scope_ids is not None:
            result['IpamScopeIds'] = self.ipam_scope_ids
        if self.ipam_scope_name is not None:
            result['IpamScopeName'] = self.ipam_scope_name
        if self.ipam_scope_type is not None:
            result['IpamScopeType'] = self.ipam_scope_type
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        result['Tags'] = []
        if self.tags is not None:
            for k in self.tags:
                result['Tags'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamScopeIds') is not None:
            self.ipam_scope_ids = m.get('IpamScopeIds')
        if m.get('IpamScopeName') is not None:
            self.ipam_scope_name = m.get('IpamScopeName')
        if m.get('IpamScopeType') is not None:
            self.ipam_scope_type = m.get('IpamScopeType')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        self.tags = []
        if m.get('Tags') is not None:
            for k in m.get('Tags'):
                temp_model = ListIpamScopesRequestTags()
                self.tags.append(temp_model.from_map(k))
        return self


class ListIpamScopesResponseBodyIpamScopesTags(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListIpamScopesResponseBodyIpamScopes(TeaModel):
    def __init__(
        self,
        create_time: str = None,
        ipam_id: str = None,
        ipam_scope_description: str = None,
        ipam_scope_id: str = None,
        ipam_scope_name: str = None,
        ipam_scope_type: str = None,
        is_default: bool = None,
        owner_id: int = None,
        pool_count: int = None,
        region_id: str = None,
        resource_group_id: str = None,
        status: str = None,
        tags: List[ListIpamScopesResponseBodyIpamScopesTags] = None,
    ):
        self.create_time = create_time
        self.ipam_id = ipam_id
        self.ipam_scope_description = ipam_scope_description
        self.ipam_scope_id = ipam_scope_id
        self.ipam_scope_name = ipam_scope_name
        self.ipam_scope_type = ipam_scope_type
        self.is_default = is_default
        self.owner_id = owner_id
        self.pool_count = pool_count
        self.region_id = region_id
        self.resource_group_id = resource_group_id
        self.status = status
        self.tags = tags

    def validate(self):
        if self.tags:
            for k in self.tags:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['CreateTime'] = self.create_time
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_scope_description is not None:
            result['IpamScopeDescription'] = self.ipam_scope_description
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.ipam_scope_name is not None:
            result['IpamScopeName'] = self.ipam_scope_name
        if self.ipam_scope_type is not None:
            result['IpamScopeType'] = self.ipam_scope_type
        if self.is_default is not None:
            result['IsDefault'] = self.is_default
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.pool_count is not None:
            result['PoolCount'] = self.pool_count
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.status is not None:
            result['Status'] = self.status
        result['Tags'] = []
        if self.tags is not None:
            for k in self.tags:
                result['Tags'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CreateTime') is not None:
            self.create_time = m.get('CreateTime')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamScopeDescription') is not None:
            self.ipam_scope_description = m.get('IpamScopeDescription')
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('IpamScopeName') is not None:
            self.ipam_scope_name = m.get('IpamScopeName')
        if m.get('IpamScopeType') is not None:
            self.ipam_scope_type = m.get('IpamScopeType')
        if m.get('IsDefault') is not None:
            self.is_default = m.get('IsDefault')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('PoolCount') is not None:
            self.pool_count = m.get('PoolCount')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('Status') is not None:
            self.status = m.get('Status')
        self.tags = []
        if m.get('Tags') is not None:
            for k in m.get('Tags'):
                temp_model = ListIpamScopesResponseBodyIpamScopesTags()
                self.tags.append(temp_model.from_map(k))
        return self


class ListIpamScopesResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipam_scopes: List[ListIpamScopesResponseBodyIpamScopes] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        self.ipam_scopes = ipam_scopes
        self.max_results = max_results
        self.next_token = next_token
        self.request_id = request_id
        self.total_count = total_count

    def validate(self):
        if self.ipam_scopes:
            for k in self.ipam_scopes:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['IpamScopes'] = []
        if self.ipam_scopes is not None:
            for k in self.ipam_scopes:
                result['IpamScopes'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipam_scopes = []
        if m.get('IpamScopes') is not None:
            for k in m.get('IpamScopes'):
                temp_model = ListIpamScopesResponseBodyIpamScopes()
                self.ipam_scopes.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamScopesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamScopesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamScopesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListIpamsRequestTags(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        # The tag key. You can specify at most 20 tag keys. The tag key cannot be an empty string.
        # 
        # The tag key can be up to 64 characters in length and can contain letters, digits, periods (.), underscores (_), and hyphens (-). The tag key must start with a letter but cannot start with `aliyun` or `acs:`. The tag key cannot contain `http://` or `https://`.
        self.key = key
        # The tag value. You can specify at most 20 tag values. The tag value can be an empty string.
        # 
        # The tag value can be up to 128 characters in length. It must start with a letter and can contain digits, periods (.), underscores (_), and hyphens (-). It cannot start with `aliyun` or `acs:`, and cannot contain `http://` or `https://`.
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListIpamsRequest(TeaModel):
    def __init__(
        self,
        ipam_ids: List[str] = None,
        ipam_name: str = None,
        max_results: int = None,
        next_token: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_group_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        tags: List[ListIpamsRequestTags] = None,
    ):
        # The IDs of IPAMs. Valid values of N: 1 to 100. A maximum of 100 IPAMs can be queried at a time.
        self.ipam_ids = ipam_ids
        # The name of the IPAM.
        # 
        # It must be 1 to 128 characters in length and cannot start with `http://` or `https://`.
        self.ipam_name = ipam_name
        # The number of entries per page. Valid values: **1** to **100**. Default value: **10**.
        self.max_results = max_results
        # The pagination token that is used in the next request to retrieve a new page of results. Valid values:
        # 
        # *   You do not need to specify this parameter for the first request.
        # *   You must specify the token that is obtained from the previous query as the value of NextToken.
        self.next_token = next_token
        self.owner_account = owner_account
        self.owner_id = owner_id
        # The ID of the region where the IPAM pool is hosted. You can call the [DescribeRegions](https://help.aliyun.com/document_detail/36063.html) operation to query the most recent region list.
        # 
        # This parameter is required.
        self.region_id = region_id
        # The resource group ID of the IPAM.
        self.resource_group_id = resource_group_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        # The tag information.
        self.tags = tags

    def validate(self):
        if self.tags:
            for k in self.tags:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.ipam_ids is not None:
            result['IpamIds'] = self.ipam_ids
        if self.ipam_name is not None:
            result['IpamName'] = self.ipam_name
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        result['Tags'] = []
        if self.tags is not None:
            for k in self.tags:
                result['Tags'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('IpamIds') is not None:
            self.ipam_ids = m.get('IpamIds')
        if m.get('IpamName') is not None:
            self.ipam_name = m.get('IpamName')
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        self.tags = []
        if m.get('Tags') is not None:
            for k in m.get('Tags'):
                temp_model = ListIpamsRequestTags()
                self.tags.append(temp_model.from_map(k))
        return self


class ListIpamsResponseBodyIpamsTags(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        # The tag key.
        self.key = key
        # The tag value.
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListIpamsResponseBodyIpams(TeaModel):
    def __init__(
        self,
        create_time: str = None,
        default_resource_discovery_association_id: str = None,
        default_resource_discovery_id: str = None,
        ipam_description: str = None,
        ipam_id: str = None,
        ipam_name: str = None,
        ipam_status: str = None,
        operating_region_list: List[str] = None,
        owner_id: int = None,
        private_default_scope_id: str = None,
        public_default_scope_id: str = None,
        region_id: str = None,
        resource_discovery_association_count: int = None,
        resource_group_id: str = None,
        scope_count: int = None,
        tags: List[ListIpamsResponseBodyIpamsTags] = None,
    ):
        # The time when the IPAM was created.
        self.create_time = create_time
        self.default_resource_discovery_association_id = default_resource_discovery_association_id
        self.default_resource_discovery_id = default_resource_discovery_id
        # The description of the IPAM.
        self.ipam_description = ipam_description
        # The ID of the IPAM.
        self.ipam_id = ipam_id
        # The name of the IPAM.
        self.ipam_name = ipam_name
        # The status of the IPAM. Valid values:
        # 
        # *   **Creating**\
        # *   **Created**\
        # *   **Deleting**\
        # *   **Deleted**\
        self.ipam_status = ipam_status
        # The effective regions of the IPAM.
        self.operating_region_list = operating_region_list
        # The Alibaba Cloud account that owns the IPAM.
        self.owner_id = owner_id
        # The default private scope created by the system after the IPAM is created.
        self.private_default_scope_id = private_default_scope_id
        # The default public scope created by the system after the IPAM is created.
        self.public_default_scope_id = public_default_scope_id
        # The region ID of the IPAM.
        self.region_id = region_id
        self.resource_discovery_association_count = resource_discovery_association_count
        # The resource group ID of the IPAM.
        self.resource_group_id = resource_group_id
        # The number of IPAM scopes. Value: **2 to 5**.
        self.scope_count = scope_count
        # The tag list.
        self.tags = tags

    def validate(self):
        if self.tags:
            for k in self.tags:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.create_time is not None:
            result['CreateTime'] = self.create_time
        if self.default_resource_discovery_association_id is not None:
            result['DefaultResourceDiscoveryAssociationId'] = self.default_resource_discovery_association_id
        if self.default_resource_discovery_id is not None:
            result['DefaultResourceDiscoveryId'] = self.default_resource_discovery_id
        if self.ipam_description is not None:
            result['IpamDescription'] = self.ipam_description
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_name is not None:
            result['IpamName'] = self.ipam_name
        if self.ipam_status is not None:
            result['IpamStatus'] = self.ipam_status
        if self.operating_region_list is not None:
            result['OperatingRegionList'] = self.operating_region_list
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.private_default_scope_id is not None:
            result['PrivateDefaultScopeId'] = self.private_default_scope_id
        if self.public_default_scope_id is not None:
            result['PublicDefaultScopeId'] = self.public_default_scope_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_discovery_association_count is not None:
            result['ResourceDiscoveryAssociationCount'] = self.resource_discovery_association_count
        if self.resource_group_id is not None:
            result['ResourceGroupId'] = self.resource_group_id
        if self.scope_count is not None:
            result['ScopeCount'] = self.scope_count
        result['Tags'] = []
        if self.tags is not None:
            for k in self.tags:
                result['Tags'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('CreateTime') is not None:
            self.create_time = m.get('CreateTime')
        if m.get('DefaultResourceDiscoveryAssociationId') is not None:
            self.default_resource_discovery_association_id = m.get('DefaultResourceDiscoveryAssociationId')
        if m.get('DefaultResourceDiscoveryId') is not None:
            self.default_resource_discovery_id = m.get('DefaultResourceDiscoveryId')
        if m.get('IpamDescription') is not None:
            self.ipam_description = m.get('IpamDescription')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamName') is not None:
            self.ipam_name = m.get('IpamName')
        if m.get('IpamStatus') is not None:
            self.ipam_status = m.get('IpamStatus')
        if m.get('OperatingRegionList') is not None:
            self.operating_region_list = m.get('OperatingRegionList')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('PrivateDefaultScopeId') is not None:
            self.private_default_scope_id = m.get('PrivateDefaultScopeId')
        if m.get('PublicDefaultScopeId') is not None:
            self.public_default_scope_id = m.get('PublicDefaultScopeId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceDiscoveryAssociationCount') is not None:
            self.resource_discovery_association_count = m.get('ResourceDiscoveryAssociationCount')
        if m.get('ResourceGroupId') is not None:
            self.resource_group_id = m.get('ResourceGroupId')
        if m.get('ScopeCount') is not None:
            self.scope_count = m.get('ScopeCount')
        self.tags = []
        if m.get('Tags') is not None:
            for k in m.get('Tags'):
                temp_model = ListIpamsResponseBodyIpamsTags()
                self.tags.append(temp_model.from_map(k))
        return self


class ListIpamsResponseBody(TeaModel):
    def __init__(
        self,
        count: int = None,
        ipams: List[ListIpamsResponseBodyIpams] = None,
        max_results: int = None,
        next_token: str = None,
        request_id: str = None,
        total_count: int = None,
    ):
        self.count = count
        # The IPAMs.
        self.ipams = ipams
        # The number of entries per page. Valid values: 1 to 100. Default value: 10.
        self.max_results = max_results
        # The pagination token that is used in the next request to retrieve a new page of results. Valid values:
        # 
        # *   If **NextToken** is empty, no next page exists.
        # *   If a value of **NextToken** is returned, the value indicates the token that is used for the next query.
        self.next_token = next_token
        # The request ID.
        self.request_id = request_id
        # The number of entries.
        self.total_count = total_count

    def validate(self):
        if self.ipams:
            for k in self.ipams:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.count is not None:
            result['Count'] = self.count
        result['Ipams'] = []
        if self.ipams is not None:
            for k in self.ipams:
                result['Ipams'].append(k.to_map() if k else None)
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        if self.total_count is not None:
            result['TotalCount'] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Count') is not None:
            self.count = m.get('Count')
        self.ipams = []
        if m.get('Ipams') is not None:
            for k in m.get('Ipams'):
                temp_model = ListIpamsResponseBodyIpams()
                self.ipams.append(temp_model.from_map(k))
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        if m.get('TotalCount') is not None:
            self.total_count = m.get('TotalCount')
        return self


class ListIpamsResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListIpamsResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListIpamsResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class ListTagResourcesRequestTag(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class ListTagResourcesRequest(TeaModel):
    def __init__(
        self,
        max_results: int = None,
        next_token: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_id: List[str] = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        resource_type: str = None,
        tag: List[ListTagResourcesRequestTag] = None,
    ):
        self.max_results = max_results
        self.next_token = next_token
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_id = resource_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        # This parameter is required.
        self.resource_type = resource_type
        self.tag = tag

    def validate(self):
        if self.tag:
            for k in self.tag:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.max_results is not None:
            result['MaxResults'] = self.max_results
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        result['Tag'] = []
        if self.tag is not None:
            for k in self.tag:
                result['Tag'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('MaxResults') is not None:
            self.max_results = m.get('MaxResults')
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        self.tag = []
        if m.get('Tag') is not None:
            for k in m.get('Tag'):
                temp_model = ListTagResourcesRequestTag()
                self.tag.append(temp_model.from_map(k))
        return self


class ListTagResourcesResponseBodyTagResources(TeaModel):
    def __init__(
        self,
        resource_id: str = None,
        resource_type: str = None,
        tag_key: str = None,
        tag_value: str = None,
    ):
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.tag_key = tag_key
        self.tag_value = tag_value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        if self.tag_key is not None:
            result['TagKey'] = self.tag_key
        if self.tag_value is not None:
            result['TagValue'] = self.tag_value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        if m.get('TagKey') is not None:
            self.tag_key = m.get('TagKey')
        if m.get('TagValue') is not None:
            self.tag_value = m.get('TagValue')
        return self


class ListTagResourcesResponseBody(TeaModel):
    def __init__(
        self,
        next_token: str = None,
        request_id: str = None,
        tag_resources: List[ListTagResourcesResponseBodyTagResources] = None,
    ):
        self.next_token = next_token
        self.request_id = request_id
        self.tag_resources = tag_resources

    def validate(self):
        if self.tag_resources:
            for k in self.tag_resources:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.next_token is not None:
            result['NextToken'] = self.next_token
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        result['TagResources'] = []
        if self.tag_resources is not None:
            for k in self.tag_resources:
                result['TagResources'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('NextToken') is not None:
            self.next_token = m.get('NextToken')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        self.tag_resources = []
        if m.get('TagResources') is not None:
            for k in m.get('TagResources'):
                temp_model = ListTagResourcesResponseBodyTagResources()
                self.tag_resources.append(temp_model.from_map(k))
        return self


class ListTagResourcesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: ListTagResourcesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = ListTagResourcesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class OpenVpcIpamServiceRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class OpenVpcIpamServiceResponseBody(TeaModel):
    def __init__(
        self,
        code: str = None,
        message: str = None,
        request_id: str = None,
    ):
        self.code = code
        self.message = message
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.code is not None:
            result['Code'] = self.code
        if self.message is not None:
            result['Message'] = self.message
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Code') is not None:
            self.code = m.get('Code')
        if m.get('Message') is not None:
            self.message = m.get('Message')
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class OpenVpcIpamServiceResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: OpenVpcIpamServiceResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = OpenVpcIpamServiceResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class TagResourcesRequestTag(TeaModel):
    def __init__(
        self,
        key: str = None,
        value: str = None,
    ):
        self.key = key
        self.value = value

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.key is not None:
            result['Key'] = self.key
        if self.value is not None:
            result['Value'] = self.value
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Key') is not None:
            self.key = m.get('Key')
        if m.get('Value') is not None:
            self.value = m.get('Value')
        return self


class TagResourcesRequest(TeaModel):
    def __init__(
        self,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_id: List[str] = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        resource_type: str = None,
        tag: List[TagResourcesRequestTag] = None,
    ):
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        # This parameter is required.
        self.resource_id = resource_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        # This parameter is required.
        self.resource_type = resource_type
        # This parameter is required.
        self.tag = tag

    def validate(self):
        if self.tag:
            for k in self.tag:
                if k:
                    k.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        result['Tag'] = []
        if self.tag is not None:
            for k in self.tag:
                result['Tag'].append(k.to_map() if k else None)
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        self.tag = []
        if m.get('Tag') is not None:
            for k in m.get('Tag'):
                temp_model = TagResourcesRequestTag()
                self.tag.append(temp_model.from_map(k))
        return self


class TagResourcesResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class TagResourcesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: TagResourcesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = TagResourcesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UntagResourcesRequest(TeaModel):
    def __init__(
        self,
        all: bool = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_id: List[str] = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
        resource_type: str = None,
        tag_key: List[str] = None,
    ):
        self.all = all
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        # This parameter is required.
        self.resource_id = resource_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id
        # This parameter is required.
        self.resource_type = resource_type
        self.tag_key = tag_key

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.all is not None:
            result['All'] = self.all
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_id is not None:
            result['ResourceId'] = self.resource_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        if self.resource_type is not None:
            result['ResourceType'] = self.resource_type
        if self.tag_key is not None:
            result['TagKey'] = self.tag_key
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('All') is not None:
            self.all = m.get('All')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceId') is not None:
            self.resource_id = m.get('ResourceId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        if m.get('ResourceType') is not None:
            self.resource_type = m.get('ResourceType')
        if m.get('TagKey') is not None:
            self.tag_key = m.get('TagKey')
        return self


class UntagResourcesResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class UntagResourcesResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UntagResourcesResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UntagResourcesResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateIpamRequest(TeaModel):
    def __init__(
        self,
        add_operating_region: List[str] = None,
        client_token: str = None,
        dry_run: bool = None,
        ipam_description: str = None,
        ipam_id: str = None,
        ipam_name: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        remove_operating_region: List[str] = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.add_operating_region = add_operating_region
        self.client_token = client_token
        self.dry_run = dry_run
        self.ipam_description = ipam_description
        # This parameter is required.
        self.ipam_id = ipam_id
        self.ipam_name = ipam_name
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.remove_operating_region = remove_operating_region
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.add_operating_region is not None:
            result['AddOperatingRegion'] = self.add_operating_region
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_description is not None:
            result['IpamDescription'] = self.ipam_description
        if self.ipam_id is not None:
            result['IpamId'] = self.ipam_id
        if self.ipam_name is not None:
            result['IpamName'] = self.ipam_name
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.remove_operating_region is not None:
            result['RemoveOperatingRegion'] = self.remove_operating_region
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AddOperatingRegion') is not None:
            self.add_operating_region = m.get('AddOperatingRegion')
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamDescription') is not None:
            self.ipam_description = m.get('IpamDescription')
        if m.get('IpamId') is not None:
            self.ipam_id = m.get('IpamId')
        if m.get('IpamName') is not None:
            self.ipam_name = m.get('IpamName')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('RemoveOperatingRegion') is not None:
            self.remove_operating_region = m.get('RemoveOperatingRegion')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class UpdateIpamResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class UpdateIpamResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateIpamResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateIpamResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateIpamPoolRequest(TeaModel):
    def __init__(
        self,
        allocation_default_cidr_mask: int = None,
        allocation_max_cidr_mask: int = None,
        allocation_min_cidr_mask: int = None,
        auto_import: bool = None,
        clear_allocation_default_cidr_mask: bool = None,
        client_token: str = None,
        dry_run: bool = None,
        ipam_pool_description: str = None,
        ipam_pool_id: str = None,
        ipam_pool_name: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.allocation_default_cidr_mask = allocation_default_cidr_mask
        self.allocation_max_cidr_mask = allocation_max_cidr_mask
        self.allocation_min_cidr_mask = allocation_min_cidr_mask
        self.auto_import = auto_import
        self.clear_allocation_default_cidr_mask = clear_allocation_default_cidr_mask
        self.client_token = client_token
        self.dry_run = dry_run
        self.ipam_pool_description = ipam_pool_description
        # This parameter is required.
        self.ipam_pool_id = ipam_pool_id
        self.ipam_pool_name = ipam_pool_name
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.allocation_default_cidr_mask is not None:
            result['AllocationDefaultCidrMask'] = self.allocation_default_cidr_mask
        if self.allocation_max_cidr_mask is not None:
            result['AllocationMaxCidrMask'] = self.allocation_max_cidr_mask
        if self.allocation_min_cidr_mask is not None:
            result['AllocationMinCidrMask'] = self.allocation_min_cidr_mask
        if self.auto_import is not None:
            result['AutoImport'] = self.auto_import
        if self.clear_allocation_default_cidr_mask is not None:
            result['ClearAllocationDefaultCidrMask'] = self.clear_allocation_default_cidr_mask
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_pool_description is not None:
            result['IpamPoolDescription'] = self.ipam_pool_description
        if self.ipam_pool_id is not None:
            result['IpamPoolId'] = self.ipam_pool_id
        if self.ipam_pool_name is not None:
            result['IpamPoolName'] = self.ipam_pool_name
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AllocationDefaultCidrMask') is not None:
            self.allocation_default_cidr_mask = m.get('AllocationDefaultCidrMask')
        if m.get('AllocationMaxCidrMask') is not None:
            self.allocation_max_cidr_mask = m.get('AllocationMaxCidrMask')
        if m.get('AllocationMinCidrMask') is not None:
            self.allocation_min_cidr_mask = m.get('AllocationMinCidrMask')
        if m.get('AutoImport') is not None:
            self.auto_import = m.get('AutoImport')
        if m.get('ClearAllocationDefaultCidrMask') is not None:
            self.clear_allocation_default_cidr_mask = m.get('ClearAllocationDefaultCidrMask')
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamPoolDescription') is not None:
            self.ipam_pool_description = m.get('IpamPoolDescription')
        if m.get('IpamPoolId') is not None:
            self.ipam_pool_id = m.get('IpamPoolId')
        if m.get('IpamPoolName') is not None:
            self.ipam_pool_name = m.get('IpamPoolName')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class UpdateIpamPoolResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class UpdateIpamPoolResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateIpamPoolResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateIpamPoolResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateIpamPoolAllocationRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_pool_allocation_description: str = None,
        ipam_pool_allocation_id: str = None,
        ipam_pool_allocation_name: str = None,
        region_id: str = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        self.ipam_pool_allocation_description = ipam_pool_allocation_description
        # This parameter is required.
        self.ipam_pool_allocation_id = ipam_pool_allocation_id
        self.ipam_pool_allocation_name = ipam_pool_allocation_name
        # This parameter is required.
        self.region_id = region_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_pool_allocation_description is not None:
            result['IpamPoolAllocationDescription'] = self.ipam_pool_allocation_description
        if self.ipam_pool_allocation_id is not None:
            result['IpamPoolAllocationId'] = self.ipam_pool_allocation_id
        if self.ipam_pool_allocation_name is not None:
            result['IpamPoolAllocationName'] = self.ipam_pool_allocation_name
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamPoolAllocationDescription') is not None:
            self.ipam_pool_allocation_description = m.get('IpamPoolAllocationDescription')
        if m.get('IpamPoolAllocationId') is not None:
            self.ipam_pool_allocation_id = m.get('IpamPoolAllocationId')
        if m.get('IpamPoolAllocationName') is not None:
            self.ipam_pool_allocation_name = m.get('IpamPoolAllocationName')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        return self


class UpdateIpamPoolAllocationResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class UpdateIpamPoolAllocationResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateIpamPoolAllocationResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateIpamPoolAllocationResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateIpamResourceDiscoveryRequest(TeaModel):
    def __init__(
        self,
        add_operating_region: List[str] = None,
        client_token: str = None,
        dry_run: bool = None,
        ipam_resource_discovery_description: str = None,
        ipam_resource_discovery_id: str = None,
        ipam_resource_discovery_name: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        remove_operating_region: List[str] = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.add_operating_region = add_operating_region
        self.client_token = client_token
        self.dry_run = dry_run
        self.ipam_resource_discovery_description = ipam_resource_discovery_description
        # This parameter is required.
        self.ipam_resource_discovery_id = ipam_resource_discovery_id
        self.ipam_resource_discovery_name = ipam_resource_discovery_name
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.remove_operating_region = remove_operating_region
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.add_operating_region is not None:
            result['AddOperatingRegion'] = self.add_operating_region
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_resource_discovery_description is not None:
            result['IpamResourceDiscoveryDescription'] = self.ipam_resource_discovery_description
        if self.ipam_resource_discovery_id is not None:
            result['IpamResourceDiscoveryId'] = self.ipam_resource_discovery_id
        if self.ipam_resource_discovery_name is not None:
            result['IpamResourceDiscoveryName'] = self.ipam_resource_discovery_name
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.remove_operating_region is not None:
            result['RemoveOperatingRegion'] = self.remove_operating_region
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AddOperatingRegion') is not None:
            self.add_operating_region = m.get('AddOperatingRegion')
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamResourceDiscoveryDescription') is not None:
            self.ipam_resource_discovery_description = m.get('IpamResourceDiscoveryDescription')
        if m.get('IpamResourceDiscoveryId') is not None:
            self.ipam_resource_discovery_id = m.get('IpamResourceDiscoveryId')
        if m.get('IpamResourceDiscoveryName') is not None:
            self.ipam_resource_discovery_name = m.get('IpamResourceDiscoveryName')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('RemoveOperatingRegion') is not None:
            self.remove_operating_region = m.get('RemoveOperatingRegion')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class UpdateIpamResourceDiscoveryResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class UpdateIpamResourceDiscoveryResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateIpamResourceDiscoveryResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateIpamResourceDiscoveryResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


class UpdateIpamScopeRequest(TeaModel):
    def __init__(
        self,
        client_token: str = None,
        dry_run: bool = None,
        ipam_scope_description: str = None,
        ipam_scope_id: str = None,
        ipam_scope_name: str = None,
        owner_account: str = None,
        owner_id: int = None,
        region_id: str = None,
        resource_owner_account: str = None,
        resource_owner_id: int = None,
    ):
        self.client_token = client_token
        self.dry_run = dry_run
        self.ipam_scope_description = ipam_scope_description
        # This parameter is required.
        self.ipam_scope_id = ipam_scope_id
        self.ipam_scope_name = ipam_scope_name
        self.owner_account = owner_account
        self.owner_id = owner_id
        # This parameter is required.
        self.region_id = region_id
        self.resource_owner_account = resource_owner_account
        self.resource_owner_id = resource_owner_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.client_token is not None:
            result['ClientToken'] = self.client_token
        if self.dry_run is not None:
            result['DryRun'] = self.dry_run
        if self.ipam_scope_description is not None:
            result['IpamScopeDescription'] = self.ipam_scope_description
        if self.ipam_scope_id is not None:
            result['IpamScopeId'] = self.ipam_scope_id
        if self.ipam_scope_name is not None:
            result['IpamScopeName'] = self.ipam_scope_name
        if self.owner_account is not None:
            result['OwnerAccount'] = self.owner_account
        if self.owner_id is not None:
            result['OwnerId'] = self.owner_id
        if self.region_id is not None:
            result['RegionId'] = self.region_id
        if self.resource_owner_account is not None:
            result['ResourceOwnerAccount'] = self.resource_owner_account
        if self.resource_owner_id is not None:
            result['ResourceOwnerId'] = self.resource_owner_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ClientToken') is not None:
            self.client_token = m.get('ClientToken')
        if m.get('DryRun') is not None:
            self.dry_run = m.get('DryRun')
        if m.get('IpamScopeDescription') is not None:
            self.ipam_scope_description = m.get('IpamScopeDescription')
        if m.get('IpamScopeId') is not None:
            self.ipam_scope_id = m.get('IpamScopeId')
        if m.get('IpamScopeName') is not None:
            self.ipam_scope_name = m.get('IpamScopeName')
        if m.get('OwnerAccount') is not None:
            self.owner_account = m.get('OwnerAccount')
        if m.get('OwnerId') is not None:
            self.owner_id = m.get('OwnerId')
        if m.get('RegionId') is not None:
            self.region_id = m.get('RegionId')
        if m.get('ResourceOwnerAccount') is not None:
            self.resource_owner_account = m.get('ResourceOwnerAccount')
        if m.get('ResourceOwnerId') is not None:
            self.resource_owner_id = m.get('ResourceOwnerId')
        return self


class UpdateIpamScopeResponseBody(TeaModel):
    def __init__(
        self,
        request_id: str = None,
    ):
        self.request_id = request_id

    def validate(self):
        pass

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.request_id is not None:
            result['RequestId'] = self.request_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')
        return self


class UpdateIpamScopeResponse(TeaModel):
    def __init__(
        self,
        headers: Dict[str, str] = None,
        status_code: int = None,
        body: UpdateIpamScopeResponseBody = None,
    ):
        self.headers = headers
        self.status_code = status_code
        self.body = body

    def validate(self):
        if self.body:
            self.body.validate()

    def to_map(self):
        _map = super().to_map()
        if _map is not None:
            return _map

        result = dict()
        if self.headers is not None:
            result['headers'] = self.headers
        if self.status_code is not None:
            result['statusCode'] = self.status_code
        if self.body is not None:
            result['body'] = self.body.to_map()
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('headers') is not None:
            self.headers = m.get('headers')
        if m.get('statusCode') is not None:
            self.status_code = m.get('statusCode')
        if m.get('body') is not None:
            temp_model = UpdateIpamScopeResponseBody()
            self.body = temp_model.from_map(m['body'])
        return self


