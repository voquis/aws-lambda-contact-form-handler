"""
Provider unit tests
"""

import os

import pytest
from moto import mock_ssm, mock_secretsmanager
import tests.unit.service.aws_utils as utils
from app_handler.provider.config import ConfigProvider

# Set boto (moto) client default values
os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'

config = ConfigProvider()

def test_invalid_names():
    """
    Assert invalid or empty names produce exceptions
    """
    # Test non-existent variable throws an exception
    with pytest.raises(ValueError) as exception:
        config.get('')

    with pytest.raises(ValueError) as env_exception:
        config.get_from_env('')

    with pytest.raises(ValueError) as ps_exception:
        config.get_from_aws_ssm_parameter_store('')

    with pytest.raises(ValueError) as sm_exception:
        config.get_from_aws_secrets_manager('')

    assert str(exception.value) == 'Invalid key name provided'
    assert str(env_exception.value) == 'Missing or empty environment key'
    assert str(ps_exception.value) == 'Missing or empty environment value for _PARAMETER_STORE_NAME'
    assert str(sm_exception.value) == 'Missing or empty environment value for _SECRETS_MANAGER_NAME'


def test_env_vars(monkeypatch):
    """
    Test Fetching config values from environment
    """

    # Test fetches from environment by default
    monkeypatch.setenv('ENV_VAR_TEST', 'test_value')
    assert config.get('ENV_VAR_TEST') == 'test_value'

    # Test non-existent variable throws an exception
    with pytest.raises(ValueError) as exception:
        config.get('NONEXISTENT_ENV_VAR')

    assert 'Missing or empty environment value' in str(exception.value)


def test_unknown_source(monkeypatch):
    """
    Test unknown source raises an exception
    """
    monkeypatch.setenv('UNKNOWN', 'test_value')
    monkeypatch.setenv('UNKNOWN_SOURCE', 'unknown')
    # Test unknown source returns nothing
    with pytest.raises(ValueError) as exception:
        config.get('UNKNOWN')

    assert 'Unknown source' in str(exception.value)


@mock_ssm
def test_aws_ssm_parameter_store_success(monkeypatch):
    """
    Test Fetching config values from parameter store
    """

    # Instruct config provider to fetch value for SSM_TEST from parameter store
    monkeypatch.setenv('SSM_OK_SOURCE', 'aws_ssm_parameter_store')

    # Create mocked test parameter to later fetch using moto
    utils.ssm_put_parameter_securestring('/is/ok', 'my val')

    # Assert value is correctly retrieved if the key name is provided
    monkeypatch.setenv('SSM_OK_PARAMETER_STORE_NAME', '/is/ok')
    assert config.get('SSM_OK') == 'my val'


@mock_ssm
def test_aws_ssm_parameter_store_no_name(monkeypatch):
    """
    Test Fetching config values from parameter store without specifying a name
    """

    monkeypatch.setenv('SSM_NONAME_SOURCE', 'aws_ssm_parameter_store')

    with pytest.raises(ValueError) as exception:
        config.get('SSM_NONAME')

    msg = 'Missing or empty environment value for SSM_NONAME_PARAMETER_STORE_NAME'
    assert str(exception.value) == msg


@mock_ssm
def test_aws_ssm_parameter_store_does_not_exist(monkeypatch):
    """
    Test Fetching non-existent config values from parameter store
    """

    monkeypatch.setenv('SSM_NONEXISTENT_SOURCE', 'aws_ssm_parameter_store')
    monkeypatch.setenv('SSM_NONEXISTENT_PARAMETER_STORE_NAME', '/does/not/exist')
    # Assert an exception is thrown if parameter name is not provided
    with pytest.raises(ValueError) as exception:
        config.get('SSM_NONEXISTENT')

    assert 'Missing or empty AWS SSM Parameter Store value ' in str(exception.value)


@mock_secretsmanager
def test_aws_secrets_manager_success(monkeypatch):
    """
    Test Fetching config values from secrets manager
    """

    # Instruct config provider to fetch value for SM_TEST from secrets manager
    monkeypatch.setenv('SECRET_OK_SOURCE', 'aws_secrets_manager')

    # Create mocked test parameter to later fetch using moto
    utils.put_secretsmanager_secret('/is/ok', 'my secret')

    # Assert value is correctly retrieved if the key name is provided
    monkeypatch.setenv('SECRET_OK_SECRETS_MANAGER_NAME', '/is/ok')
    assert config.get('SECRET_OK') == 'my secret'


@mock_secretsmanager
def test_aws_secrets_manager_no_name(monkeypatch):
    """
    Test Fetching config values from secrets manager without specifying a name
    """

    monkeypatch.setenv('SECRET_NONAME_SOURCE', 'aws_secrets_manager')

    with pytest.raises(ValueError) as exception:
        config.get('SECRET_NONAME')

    msg = 'Missing or empty environment value for SECRET_NONAME_SECRETS_MANAGER_NAME'
    assert str(exception.value) == msg


@mock_secretsmanager
def test_aws_secrets_manager_does_not_exist(monkeypatch):
    """
    Test Fetching non-existent config values from secrets manager
    """

    monkeypatch.setenv('SECRET_NONEXISTENT_SOURCE', 'aws_secrets_manager')
    monkeypatch.setenv('SECRET_NONEXISTENT_SECRETS_MANAGER_NAME', '/does/not/exist')
    # Assert an exception is thrown if secret name is not provided
    with pytest.raises(ValueError) as exception:
        config.get('SECRET_NONEXISTENT')

    msg = 'Missing or empty AWS Secrets Manager value for /does/not/exist'
    assert str(exception.value) == msg
