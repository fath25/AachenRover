import argparse
import ast
import importlib.util
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'create_package.py'
spec = importlib.util.spec_from_file_location('generator', SCRIPT)
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)


@pytest.mark.parametrize('language', ['python', 'cpp'])
@pytest.mark.parametrize('kind', ['node', 'camera'])
def test_packages(tmp_path, language, kind):
    package = generator.create_package('test_worker', language, kind, destination=tmp_path,
                                       dependencies=['std_msgs'])
    manifest = ET.parse(package / 'package.xml').getroot()
    assert manifest.findtext('name') == 'test_worker'
    assert 'std_msgs' in [entry.text for entry in manifest.findall('depend')]
    for path in package.rglob('*.py'):
        ast.parse(path.read_text())
    if language == 'python':
        assert not manifest.findall('buildtool_depend')
        assert '$base/lib/test_worker' in (package / 'setup.cfg').read_text()
        assert (package / 'resource/test_worker').exists()
    else:
        assert '${PROJECT_NAME}' in (package / 'CMakeLists.txt').read_text()
    original = {p.relative_to(package): p.read_bytes() for p in package.rglob('*') if p.is_file()}
    with pytest.raises(FileExistsError):
        generator.create_package('test_worker', destination=tmp_path)
    assert original == {p.relative_to(package): p.read_bytes() for p in package.rglob('*') if p.is_file()}


@pytest.mark.parametrize('name', ['../escape', '/absolute', 'Bad-name', 'class', 'a;echo', ''])
def test_reject_invalid_name(tmp_path, name):
    with pytest.raises(argparse.ArgumentTypeError):
        generator.create_package(name, destination=tmp_path)
    assert not list(tmp_path.iterdir())


def test_refuse_dangling_symlink(tmp_path):
    (tmp_path / 'existing').symlink_to(tmp_path / 'missing')
    with pytest.raises(FileExistsError):
        generator.create_package('existing', destination=tmp_path)
