import pytest
from fastapi import HTTPException
from app.workspace import safe_path,validate_proposal
from app.intelligence import _extract

def test_safe_file_paths(tmp_path):
    assert safe_path(tmp_path,'app/main.py') == tmp_path/'app/main.py'
    for name in ['../.env','app/../main.py','.env','test.exe','dir/.ssh/id_rsa','/etc/passwd','x\\bad.py','foo/.git/config']:
        with pytest.raises(HTTPException): safe_path(tmp_path,name)

def test_proposal_checks(tmp_path):
    payload = {'files':[{'path':'foo.py','content':'print(1)'}]}
    check = validate_proposal(tmp_path,payload)
    assert check[0]['new'] is True
    with pytest.raises(HTTPException): validate_proposal(tmp_path,{'files':payload['files']*2})

def test_model_text_extraction():
    assert _extract({'output':[{'type':'message','content':[{'type':'output_text','text':'hello'}]}]})=='hello'
