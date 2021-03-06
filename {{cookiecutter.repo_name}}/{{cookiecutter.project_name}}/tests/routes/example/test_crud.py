"""
Example CRUD routes tests.

Tests are sunny day cases under the assumption that framework conventions
handle most error conditions.

"""
from json import dumps, loads

from hamcrest import (
    assert_that,
    contains,
    equal_to,
    is_,
)
from microcosm_flask.matchers import json_for
from microcosm_postgres.context import SessionContext, transaction
from microcosm_postgres.operations import recreate_all
from microcosm_postgres.identifiers import new_object_id
from mock import patch

from {{ cookiecutter.project_name }}.app import create_app
from {{ cookiecutter.project_name }}.models.example_model import Example
from {{ cookiecutter.project_name }}.tests.routes.matchers import matches_example


class TestExampleRoutes(object):

    def setup(self):
        self.graph = create_app(testing=True)
        self.client = self.graph.flask.test_client()
        recreate_all(self.graph)

        self.name1 = "name1"

        self.example1 = Example(
            id=new_object_id(),
            name=self.name1,
        )

    def teardown(self):
        self.graph.postgres.dispose()

    def test_search(self):
        with SessionContext(self.graph), transaction():
            self.example1.create()

        uri = "/api/v1/example"

        response = self.client.get(uri)

        with self.graph.app.test_request_context():
            assert_that(response.status_code, is_(equal_to(200)))
            data = loads(response.data.decode("utf-8"))
            assert_that(data["items"], contains(matches_example(self.example1)))

    def test_create(self):
        uri = "/api/v1/example"

        with patch.object(self.graph.example_store, "new_object_id") as mocked:
            mocked.return_value = self.example1.id
            response = self.client.post(uri, data=dumps({
                "name": self.example1.name,
            }))

        with self.graph.app.test_request_context():
            assert_that(response.status_code, is_(equal_to(201)))
            assert_that(json_for(response.data.decode("utf-8")), matches_example(self.example1))

    def test_replace_with_new(self):
        uri = "/api/v1/example/{}".format(self.example1.id)

        response = self.client.put(uri, data=dumps({
            "name": self.example1.name,
        }))

        with self.graph.app.test_request_context():
            assert_that(response.status_code, is_(equal_to(200)))
            assert_that(json_for(response.data.decode("utf-8")), matches_example(self.example1))

    def test_retrieve(self):
        with SessionContext(self.graph), transaction():
            self.example1.create()

        uri = "/api/v1/example/{}".format(self.example1.id)

        response = self.client.get(uri)

        with self.graph.app.test_request_context():
            assert_that(response.status_code, is_(equal_to(200)))
            assert_that(json_for(response.data.decode("utf-8")), matches_example(self.example1))

    def test_delete(self):
        with SessionContext(self.graph), transaction():
            self.example1.create()

        uri = "/api/v1/example/{}".format(self.example1.id)

        response = self.client.delete(uri)
        assert_that(response.status_code, is_(equal_to(204)))
