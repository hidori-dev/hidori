from hawkey.package import Package

class RPMTransaction:
    install_set: set[Package]
