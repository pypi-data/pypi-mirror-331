r'''
# `data_databricks_budget_policies`

Refer to the Terraform Registry for docs: [`data_databricks_budget_policies`](https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class DataDatabricksBudgetPolicies(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPolicies",
):
    '''Represents a {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies databricks_budget_policies}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies databricks_budget_policies} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__308da16ebe59212b718d934ee0e554476963cda8437b126ae712fb69aa0098f4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataDatabricksBudgetPoliciesConfig(
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DataDatabricksBudgetPolicies resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDatabricksBudgetPolicies to import.
        :param import_from_id: The id of the existing DataDatabricksBudgetPolicies that should be imported. Refer to the {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDatabricksBudgetPolicies to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10a3489902124f50cc9b08b5a351de39c98e08ea506ef50a30b5ea03bde0b936)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="budgetPolicies")
    def budget_policies(self) -> "DataDatabricksBudgetPoliciesBudgetPoliciesList":
        return typing.cast("DataDatabricksBudgetPoliciesBudgetPoliciesList", jsii.get(self, "budgetPolicies"))


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesBudgetPolicies",
    jsii_struct_bases=[],
    name_mapping={"custom_tags": "customTags", "policy_name": "policyName"},
)
class DataDatabricksBudgetPoliciesBudgetPolicies:
    def __init__(
        self,
        *,
        custom_tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param custom_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#custom_tags DataDatabricksBudgetPolicies#custom_tags}.
        :param policy_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#policy_name DataDatabricksBudgetPolicies#policy_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aff52e0097d2878ac95b424be0d6fa4116ae65b5136ff2bf87ed9cb54f075e36)
            check_type(argname="argument custom_tags", value=custom_tags, expected_type=type_hints["custom_tags"])
            check_type(argname="argument policy_name", value=policy_name, expected_type=type_hints["policy_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if custom_tags is not None:
            self._values["custom_tags"] = custom_tags
        if policy_name is not None:
            self._values["policy_name"] = policy_name

    @builtins.property
    def custom_tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags"]]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#custom_tags DataDatabricksBudgetPolicies#custom_tags}.'''
        result = self._values.get("custom_tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags"]]], result)

    @builtins.property
    def policy_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#policy_name DataDatabricksBudgetPolicies#policy_name}.'''
        result = self._values.get("policy_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksBudgetPoliciesBudgetPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags:
    def __init__(
        self,
        *,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#key DataDatabricksBudgetPolicies#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#value DataDatabricksBudgetPolicies#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ae8e3214af16019d45438f1b3f43c183363bb4fbae732a4dafedf26cb7f5c68)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#key DataDatabricksBudgetPolicies#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/databricks/databricks/1.69.0/docs/data-sources/budget_policies#value DataDatabricksBudgetPolicies#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cf8a71ca21faaf3e95bc3d42e5b597aa5be04836474e100cdd6ebf7b8bb0def)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27c3c87587caf39e3e56ee420426853cbecc48f223c7fcb8cf018b2e3ceaefcb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0621b404969ba2399e8ccf0948ebbf6006d96568da6548fa3aa43a923d30a91e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__867955174494ed86fbfee4e11f9208f3a51fbe3f8de9c8456ccb74f73e4c43b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4bc677a3c2c5af2d81421457a08e7ceb58b2f00bfd0489279a4adea8b1512e57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a7745a98816251734c465e1d7828d0a33383e1f3ba9c354bef911a51f58cd20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4f837059065cba8005c61daf9bec6fa9e1fb8ec75a54c618005757ee95d29bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__421050911b0f91c36e2a6a0b5ca9406f9df020a2ba07fdc6c0e7b72f065de4fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2993ade65bda898b77b69111a58d998c62e506825afff07a6e0568153e565f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b85b6c18569793700f18f8c74931efa660dea4d6437b22ffdacf69e2e8ea1e88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksBudgetPoliciesBudgetPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesBudgetPoliciesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30c98216d8091748f9ad73843528b65f994dd3f68ea475f35d1bcf4586b58dd4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDatabricksBudgetPoliciesBudgetPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81bc95107c1f56924de0d71d064b20dd5df3252f90fd11b53ee24158dffe64bc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDatabricksBudgetPoliciesBudgetPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c812c9b3ee2d3298da41fc60586fb5510b1c98250955a72b32d87438464fca1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f3c7967d06181552d6d29fe40b3ed1076453a595ebfd0ba555306a83d426a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46ba5d771ab319270895a5f45758d2e1a1c26d49fa037ea777436eb89b74c24a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPolicies]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPolicies]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPolicies]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ed524d82540581bb3de0072f0878962a60666b96324ee41f2de2bd2b21f3d82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDatabricksBudgetPoliciesBudgetPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesBudgetPoliciesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27fffc2a98ccaae21da23463dd528998072f398ce0fd3279d87e5844c8d0b205)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCustomTags")
    def put_custom_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0a086a50f8127a433e864009b9bac71a16c90c8c862d031c8d314f97cd40586)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCustomTags", [value]))

    @jsii.member(jsii_name="resetCustomTags")
    def reset_custom_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomTags", []))

    @jsii.member(jsii_name="resetPolicyName")
    def reset_policy_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyName", []))

    @builtins.property
    @jsii.member(jsii_name="customTags")
    def custom_tags(self) -> DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsList:
        return typing.cast(DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsList, jsii.get(self, "customTags"))

    @builtins.property
    @jsii.member(jsii_name="policyId")
    def policy_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyId"))

    @builtins.property
    @jsii.member(jsii_name="customTagsInput")
    def custom_tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]]], jsii.get(self, "customTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="policyNameInput")
    def policy_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "policyNameInput"))

    @builtins.property
    @jsii.member(jsii_name="policyName")
    def policy_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "policyName"))

    @policy_name.setter
    def policy_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76692b896e51ef439856f926fd1d65a8a9418b1fb4d3132371d0824cf41dd219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "policyName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDatabricksBudgetPoliciesBudgetPolicies]:
        return typing.cast(typing.Optional[DataDatabricksBudgetPoliciesBudgetPolicies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDatabricksBudgetPoliciesBudgetPolicies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a148da360d638fb027e36789041401b18b9f49f9d6f4745fa13132b0e24a39e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-databricks.dataDatabricksBudgetPolicies.DataDatabricksBudgetPoliciesConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
    },
)
class DataDatabricksBudgetPoliciesConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86427756d710f34c670ab4cacfd03541ec68d5fd6a5cfa4e7db19b280e1d0a10)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDatabricksBudgetPoliciesConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DataDatabricksBudgetPolicies",
    "DataDatabricksBudgetPoliciesBudgetPolicies",
    "DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags",
    "DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsList",
    "DataDatabricksBudgetPoliciesBudgetPoliciesCustomTagsOutputReference",
    "DataDatabricksBudgetPoliciesBudgetPoliciesList",
    "DataDatabricksBudgetPoliciesBudgetPoliciesOutputReference",
    "DataDatabricksBudgetPoliciesConfig",
]

publication.publish()

def _typecheckingstub__308da16ebe59212b718d934ee0e554476963cda8437b126ae712fb69aa0098f4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10a3489902124f50cc9b08b5a351de39c98e08ea506ef50a30b5ea03bde0b936(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aff52e0097d2878ac95b424be0d6fa4116ae65b5136ff2bf87ed9cb54f075e36(
    *,
    custom_tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ae8e3214af16019d45438f1b3f43c183363bb4fbae732a4dafedf26cb7f5c68(
    *,
    key: builtins.str,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cf8a71ca21faaf3e95bc3d42e5b597aa5be04836474e100cdd6ebf7b8bb0def(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27c3c87587caf39e3e56ee420426853cbecc48f223c7fcb8cf018b2e3ceaefcb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0621b404969ba2399e8ccf0948ebbf6006d96568da6548fa3aa43a923d30a91e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__867955174494ed86fbfee4e11f9208f3a51fbe3f8de9c8456ccb74f73e4c43b2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bc677a3c2c5af2d81421457a08e7ceb58b2f00bfd0489279a4adea8b1512e57(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a7745a98816251734c465e1d7828d0a33383e1f3ba9c354bef911a51f58cd20(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4f837059065cba8005c61daf9bec6fa9e1fb8ec75a54c618005757ee95d29bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__421050911b0f91c36e2a6a0b5ca9406f9df020a2ba07fdc6c0e7b72f065de4fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2993ade65bda898b77b69111a58d998c62e506825afff07a6e0568153e565f3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b85b6c18569793700f18f8c74931efa660dea4d6437b22ffdacf69e2e8ea1e88(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30c98216d8091748f9ad73843528b65f994dd3f68ea475f35d1bcf4586b58dd4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81bc95107c1f56924de0d71d064b20dd5df3252f90fd11b53ee24158dffe64bc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c812c9b3ee2d3298da41fc60586fb5510b1c98250955a72b32d87438464fca1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87f3c7967d06181552d6d29fe40b3ed1076453a595ebfd0ba555306a83d426a9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46ba5d771ab319270895a5f45758d2e1a1c26d49fa037ea777436eb89b74c24a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ed524d82540581bb3de0072f0878962a60666b96324ee41f2de2bd2b21f3d82(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDatabricksBudgetPoliciesBudgetPolicies]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27fffc2a98ccaae21da23463dd528998072f398ce0fd3279d87e5844c8d0b205(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0a086a50f8127a433e864009b9bac71a16c90c8c862d031c8d314f97cd40586(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDatabricksBudgetPoliciesBudgetPoliciesCustomTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76692b896e51ef439856f926fd1d65a8a9418b1fb4d3132371d0824cf41dd219(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a148da360d638fb027e36789041401b18b9f49f9d6f4745fa13132b0e24a39e(
    value: typing.Optional[DataDatabricksBudgetPoliciesBudgetPolicies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86427756d710f34c670ab4cacfd03541ec68d5fd6a5cfa4e7db19b280e1d0a10(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass
