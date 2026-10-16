import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from starlette.requests import Request
from app.api.routers import retrieval as router
from app.api.dependencies import workspace
from app.infrastructure.rag.retrieval import RetrievalService


class IndexedDocumentsTests(unittest.IsolatedAsyncioTestCase):
    async def test_unauthorized_workspace_never_reads_documents(self):
        with patch.object(router, 'authorize_workspace', AsyncMock(side_effect=HTTPException(404))), \
             patch.object(router.RetrievalService, 'list_documents', AsyncMock()) as read:
            with self.assertRaises(HTTPException):
                await router.list_documents(SimpleNamespace(sub='viewer'), 'other-workspace')
            read.assert_not_awaited()

    async def test_listing_filters_workspace_and_upload_namespace(self):
        result = MagicMock()
        result.mappings.return_value.all.return_value = [
            {'repo_id': 'knowledge:abc', 'file_path': 'layout.tsx', 'indexed_chunks': 2}
        ]
        db = AsyncMock()
        db.execute.return_value = result
        session = MagicMock()
        session.__aenter__ = AsyncMock(return_value=db)
        session.__aexit__ = AsyncMock(return_value=False)
        with patch('app.infrastructure.rag.retrieval.async_session_factory', return_value=session):
            documents = await RetrievalService().list_documents('workspace-a')
        sql, params = db.execute.await_args.args
        self.assertIn('workspace_id=:ws', str(sql))
        self.assertIn("repo_id LIKE 'knowledge:%'", str(sql))
        self.assertEqual(params, {'ws': 'workspace-a'})
        self.assertEqual(documents, [{'document_id': 'abc', 'filename': 'layout.tsx', 'indexed_chunks': 2}])

    async def test_json_header_on_get_does_not_parse_an_empty_body(self):
        request = Request({'type': 'http', 'method': 'GET',
                           'path': '/v1/knowledge/list/workspace-a',
                           'path_params': {'workspace_id': 'workspace-a'},
                           'query_string': b'', 'headers': [(b'content-type', b'application/json')]})
        user = SimpleNamespace(sub='viewer')
        with patch.object(workspace, 'authorize_workspace', AsyncMock()) as authorize:
            await workspace.authorize_knowledge_request(request, user)
        authorize.assert_awaited_once_with(user, 'workspace-a')
