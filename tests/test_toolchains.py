from fastapi import HTTPException
from app.toolchains import list_profiles,run_verification
import pytest

def test_toolchain_profiles_and_unknown(tmp_path):
    assert {x['id'] for x in list_profiles()} == {'python-syntax','javascript-syntax'}
    with pytest.raises(HTTPException) as exc:
        run_verification(tmp_path,'arbitrary-command')
    assert exc.value.status_code == 422
    with pytest.raises(HTTPException) as exc:
        run_verification(tmp_path,'python-syntax')
    assert exc.value.status_code == 422
