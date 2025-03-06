"""SpeeDBeeSynapse custom component development environment tool."""
import copy
import importlib.resources
import json
import uuid
import warnings
from pathlib import Path

from . import resources as sccde_resources
from . import utils

SCC_INFO = {
    'package-name': '',
    'package-version': '0.1.0',
    'package-uuid': '',
    'package-description': 'Your package descrition here',
    'python-components-source-dir': 'source/python',
    'author': '',
    'license': '',
    'license-file': '',
    'components': {},
}


def add_sample(info_path: Path, sample_lang: str, sample_type: str) -> None:
    """Add sample into the current environment."""
    if sample_lang == 'none':
        return

    # 環境情報ファイルを読み込み
    with info_path.open(mode='rt') as fo:
        info = json.load(fo)

    # 追加するサンプルのUUIDの生成、ファイル名サフィックスの決定
    suffix_num = len(info['components']) + 1
    new_uuid = str(uuid.uuid4())

    if sample_lang == 'python':
        # Python用のディレクトリの準備
        python_dir = info_path.parent / info['python-components-source-dir']
        python_dir.mkdir(parents=True, exist_ok=True)

        # Pythonカスタムコンポーネントサンプルのコピー
        with (python_dir / f'sample_{sample_type}_{suffix_num}.py').open(mode='w', encoding='utf-8') as fo:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                content = importlib.resources.read_text(sccde_resources, f'sample_{sample_type}.py')
                content = content.replace('{{REPLACED-UUID}}', new_uuid)
            fo.write(content)

        # カスタムUIファイルのコピー
        parameter_ui_dir = info_path.parent / f'parameter_ui/sample_{sample_type}_{suffix_num}'
        parameter_ui_dir.mkdir(parents=True, exist_ok=True)
        with (parameter_ui_dir / 'custom_ui.json').open(mode='w', encoding='utf-8') as fo:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                content = importlib.resources.read_text(sccde_resources, f'sample_{sample_type}_ui.json')
            fo.write(content)

        # 環境情報ファイルの更新
        info['components'][new_uuid] = {
            'name': f'Sample {sample_type}',
            'description': '',
            'component-type': 'python',
            'modulename': f'sample_{sample_type}_{suffix_num}',
            'parameter-ui-type': 'json',
            'parameter-ui': f'parameter_ui/sample_{sample_type}_{suffix_num}/custom_ui.json',
        }

    elif sample_lang == 'c':
        utils.print_error('c component sample is not supported now')

    # 環境情報ファイルの出力
    with info_path.open(mode='wt') as fo:
        json.dump(info, fo, ensure_ascii=False, indent=2)
        fo.write('\n')


def init(info_path: Path, package_name: str, sample_lang: str, sample_type: str) -> None:
    """Initialize resource repogitory."""
    with info_path.open(mode='wt') as fo:
        info = copy.deepcopy(SCC_INFO)
        info['package-name'] = package_name
        info['package-uuid'] = str(uuid.uuid4())

        json.dump(info, fo, ensure_ascii=False, indent=2)
        fo.write('\n')

    add_sample(info_path, sample_lang, sample_type)
