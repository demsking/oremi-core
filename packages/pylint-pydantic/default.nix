{
  lib,
  buildPythonPackage,
  fetchFromGitHub,
  callPackage,
  setuptools,
  pylint,
  pylint-plugin-utils,
  pydantic,
  email-validator,
  pythonOlder,
  pytestCheckHook,
  dirty-equals,
  pytest-examples,
  pytest-mock,
  faker,
}:
buildPythonPackage rec {
  pname = "pylint-pydantic";
  version = "0.2.4";
  format = "pyproject";

  src = fetchFromGitHub {
    owner = "fcfangcc";
    repo = "pylint-pydantic";
    rev = version;
    hash = "sha256-jUo9w6OvrkpdJdcf8UBEC46Be8wx9YeNB09LOA3trOQ=";
  };

  patches = [];

  nativeBuildInputs = [
    pylint
    pydantic
    setuptools
    pylint-plugin-utils
  ];

  meta = with lib; {
    description = "A Pylint plugin to help Pylint understand the Pydantic";
    homepage = "https://github.com/fcfangcc/pylint-pydantic";
    changelog = "https://github.com/fcfangcc/pylint-pydantic/blob/${version}/README.rst#changelog";
    license = licenses.lgpl3Plus;
    maintainers = with maintainers; [ ]; # TODO how to add new maintainers?
  };
}
