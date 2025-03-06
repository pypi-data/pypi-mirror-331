r'''
# @matthewbonig/secrets

The AWS Secrets Manager [Secret](https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_secretsmanager.Secret.html) construct has a big footgun, **if you update the `generateSecretString` property, the secret gets recreated!**
This isn't exactly a flaw of the CDK, but of how CloudFormation handles this property.

So, this library has a single construct with a single intention, to allow you to update the `generateSecretString` property without recreating the secret.

> [!WARNING]
> If you have an existing aws-cdk-lib/aws_secretsmanager.Secret, you can replace it with this new construct. However,
> when you update your stack the existing value will be completely wiped out and re-created using the new construct.
> Make a backup of your secret before using this new construct on an existing secret.

## Design Philosophy

Secrets are the AWS-preferred method for passing configuration values to runtime components. However, with the existing
secret it's painful to manage the contents of a secret over the life of a project. You can't provide all your configuration
values directly in your `generateSecretString` property because you'll then likely expose sensitive
IaC. However, you also can't just leave this field completely blank because it will either make post-deployment changes
to the secret more error-prone (as someone may manually enter in field names incorrectly) or it will make it impossible
for some services to work at all until a post-deployment change is made, like ECS.

So, this construct is designed to make it so you can update the `generateSecretString` property without recreating the secret.
This allows you to define the basic shape of a secret through your IaC ensuring that post-deployment updates are done
with fewer errors.

It is a fundamental principle of this construct that:

* The values stored in secrets are required to be updated manually outside of the IaC process.
* The shape of the secret is defined in the IaC process.
* Changes to the shape of the secret are made through the IaC process.
* Changes to the shape and values of the secret in IaC do not affect fields and values that were not changed in IaC.
* Changes made to the value of the secret through an outside process are retained unless explicitly changed through IaC.

## Usage

```python
import { Secret } from '@matthewbonig/secrets';
// ....
new Secret(this, 'MySecret', {
  generateSecretString: {
    generateStringKey: 'password',
    secretStringTemplate: JSON.stringify({
      username: 'my-username',
      password: 'some-password',
    }),
  },
});
```

This is a drop-in replacement, and has the same API surface area as the original `aws_secretsmanager.Secret` construct. The difference is that the `generateSecretString` property can be updated without recreating the secret.

There are a few different scenarios when you make changes to the `generateSecretString` property:

1. **No change**: If you don't change the `generateSecretString` property, the secret will not be updated.
2. **Change**: If you change the `generateSecretString` property, by adding a new property, the secret will be updated, and only the new property will be changed. For example, if you add 'api-key' to the object then the secret will get the additional 'api-key' field added to it and all other properties will not be affected.
3. **Change**: If you update the value of an existing property on the `generateSecretString` property, the secret will be updated, and only the updated property will be changed. For example, if you change the value of 'password' to a new value, then only the 'password' property will be updated on the secret.
4. **Change**: If you change the `generateStringKey` field, then a new field will be added to the secret. The previously generated field will not be removed from the secret.
5. **Change**: If you change any of the properties that define how the `generateStringKey` should be generated, like the `excludePunctuation` property, then the field specified by the `generateStringKey` will be regenerated with the new parameters and the other fields will remain unchanged.
6. **Remove**: If you remove a property from the `generateSecretString` property, the secret will be updated, and the property will be removed from the secret and all other properties will remain unchanged.

## Example

Let's begin with a simple secret with two fields, `username` and `password`.

```python
new Secret(this, 'MySecret', {
  generateSecretString: {
    generateStringKey: 'password',
    secretStringTemplate: JSON.stringify({
      username: 'my-username',
      password: 'some-password',
    }),
  },
});
```

You can update the fields manually. Let's say you update the password field:

```json
{
  "username": "my-username",
  "password": "new-password"
}
```

Later, you update the Secret and add a new field to the `generateSecretString` property:

```python
new Secret(this, 'MySecret', {
  generateSecretString: {
    generateStringKey: 'password',
    secretStringTemplate: JSON.stringify({
      username: 'my-username',
      password: 'some-password',
      someNewField: 'some-new-value',
    }),
  },
});
```

When deployed, the `someNewField` will be added to the secret but the other fields will remain unchanged.

Later on, you can also update the `generateSecretString` property and update an existing field:

```python
new Secret(this, 'MySecret', {
  generateSecretString: {
    generateStringKey: 'password',
    secretStringTemplate: JSON.stringify({
      username: 'my-username',
      password: 'some-new-password',
      someNewField: 'some-new-value',
    }),
  },
});
```

Now the value for `password` will be updated to the new value without changing the values of `username` or `someNewField`.

Finally, you can remove a field from the `generateSecretString` property, like `someNewField`:

```python
new Secret(this, 'MySecret', {
  generateSecretString: {
    generateStringKey: 'password',
    secretStringTemplate: JSON.stringify({
      username: 'my-username',
      password: 'some-new-password',
    }),
  },
```

The value will be removed from the secret without affecting the other fields.
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

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


class Secret(
    _aws_cdk_aws_secretsmanager_ceddda9d.Secret,
    metaclass=jsii.JSIIMeta,
    jsii_type="@matthewbonig/secret.Secret",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        generate_secret_string: typing.Optional[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.SecretStringGenerator, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        replica_regions: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ReplicaRegion, typing.Dict[builtins.str, typing.Any]]]] = None,
        secret_name: typing.Optional[builtins.str] = None,
        secret_object_value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.SecretValue]] = None,
        secret_string_beta1: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.SecretStringValueBeta1] = None,
        secret_string_value: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: An optional, human-friendly description of the secret. Default: - No description.
        :param encryption_key: The customer-managed encryption key to use for encrypting the secret value. Default: - A default KMS key for the account and region is used.
        :param generate_secret_string: Configuration for how to generate a secret value. Only one of ``secretString`` and ``generateSecretString`` can be provided. Default: - 32 characters with upper-case letters, lower-case letters, punctuation and numbers (at least one from each category), per the default values of ``SecretStringGenerator``.
        :param removal_policy: Policy to apply when the secret is removed from this stack. Default: - Not set.
        :param replica_regions: A list of regions where to replicate this secret. Default: - Secret is not replicated
        :param secret_name: A name for the secret. Note that deleting secrets from SecretsManager does not happen immediately, but after a 7 to 30 days blackout period. During that period, it is not possible to create another secret that shares the same name. Default: - A name is generated by CloudFormation.
        :param secret_object_value: Initial value for a JSON secret. **NOTE:** *It is **highly** encouraged to leave this field undefined and allow SecretsManager to create the secret value. The secret object -- if provided -- will be included in the output of the cdk as part of synthesis, and will appear in the CloudFormation template in the console. This can be secure(-ish) if that value is merely reference to another resource (or one of its attributes), but if the value is a plaintext string, it will be visible to anyone with access to the CloudFormation template (via the AWS Console, SDKs, or CLI). Specifies a JSON object that you want to encrypt and store in this new version of the secret. To specify a simple string value instead, use ``SecretProps.secretStringValue`` Only one of ``secretStringBeta1``, ``secretStringValue``, 'secretObjectValue', and ``generateSecretString`` can be provided. Default: - SecretsManager generates a new secret value.
        :param secret_string_beta1: (deprecated) Initial value for the secret. **NOTE:** *It is **highly** encouraged to leave this field undefined and allow SecretsManager to create the secret value. The secret string -- if provided -- will be included in the output of the cdk as part of synthesis, and will appear in the CloudFormation template in the console. This can be secure(-ish) if that value is merely reference to another resource (or one of its attributes), but if the value is a plaintext string, it will be visible to anyone with access to the CloudFormation template (via the AWS Console, SDKs, or CLI). Specifies text data that you want to encrypt and store in this new version of the secret. May be a simple string value, or a string representation of a JSON structure. Only one of ``secretStringBeta1``, ``secretStringValue``, and ``generateSecretString`` can be provided. Default: - SecretsManager generates a new secret value.
        :param secret_string_value: Initial value for the secret. **NOTE:** *It is **highly** encouraged to leave this field undefined and allow SecretsManager to create the secret value. The secret string -- if provided -- will be included in the output of the cdk as part of synthesis, and will appear in the CloudFormation template in the console. This can be secure(-ish) if that value is merely reference to another resource (or one of its attributes), but if the value is a plaintext string, it will be visible to anyone with access to the CloudFormation template (via the AWS Console, SDKs, or CLI). Specifies text data that you want to encrypt and store in this new version of the secret. May be a simple string value. To provide a string representation of JSON structure, use ``SecretProps.secretObjectValue`` instead. Only one of ``secretStringBeta1``, ``secretStringValue``, 'secretObjectValue', and ``generateSecretString`` can be provided. Default: - SecretsManager generates a new secret value.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b33736f6f9f8446e6307fdf4cf808df1d59ea1cf3ef5b76ec30fbc87f05b2d01)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = _aws_cdk_aws_secretsmanager_ceddda9d.SecretProps(
            description=description,
            encryption_key=encryption_key,
            generate_secret_string=generate_secret_string,
            removal_policy=removal_policy,
            replica_regions=replica_regions,
            secret_name=secret_name,
            secret_object_value=secret_object_value,
            secret_string_beta1=secret_string_beta1,
            secret_string_value=secret_string_value,
        )

        jsii.create(self.__class__, self, [scope, id, props])


__all__ = [
    "Secret",
]

publication.publish()

def _typecheckingstub__b33736f6f9f8446e6307fdf4cf808df1d59ea1cf3ef5b76ec30fbc87f05b2d01(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    description: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    generate_secret_string: typing.Optional[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.SecretStringGenerator, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    replica_regions: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_secretsmanager_ceddda9d.ReplicaRegion, typing.Dict[builtins.str, typing.Any]]]] = None,
    secret_name: typing.Optional[builtins.str] = None,
    secret_object_value: typing.Optional[typing.Mapping[builtins.str, _aws_cdk_ceddda9d.SecretValue]] = None,
    secret_string_beta1: typing.Optional[_aws_cdk_aws_secretsmanager_ceddda9d.SecretStringValueBeta1] = None,
    secret_string_value: typing.Optional[_aws_cdk_ceddda9d.SecretValue] = None,
) -> None:
    """Type checking stubs"""
    pass
