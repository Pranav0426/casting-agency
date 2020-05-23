import os
import unittest
import json

from app import create_app
from models import setup_db, Movie, Actor

# Tokens are formatted as such to limit lenght on a line
CASTING_ASSISTANT = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNva1hNOFJVX05xWExzUjRqNTlzUiJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHktc2hvcC5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWVjNGVhODczZjg0Y2MwYzYwNGE1MGVjIiwiYXVkIjpbImFnZW5jeSIsImh0dHBzOi8vdWRhY2l0eS1zaG9wLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE1ODk5ODY1MjEsImV4cCI6MTU5MDA3MjkyMSwiYXpwIjoiZUg5QXBvRVZsaVliZ3pOWlVWN2ZnNXNOc3dwZDdxcXMiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiZ2V0OmFjdG9ycyIsImdldDptb3ZpZXMiXX0.trbQXZd1qQGlzTG-c42vBkS7hijBukjeJtTTIa9RVcjUQJPEUkkUZ8Zo3laacWvXKjdGCGeTO2EsNMxgtNUJFkugqRoR0fNudUOwSpjn4k4J-Y6ZnF5TqwI8P7LTLcVugAX5IDuV5LQlDJE9OCWQ3GE2_LKrteJPZu46fr7dYIJGJ7ardioqX029ZMCzrnpst9i9WZa-M0-A_WvYBp2e4I_TjoFyEH7xQZuOERRruEd7rwoycmCWuJd_Q90_SPVMAjMjLMjb_8e43EmnAcvySV53-NPDi35bIgHaTrofZI8ykj6bb6u_BW0Xebn0JkxtuT8FmaYX_cCalBXR-QJbCw')  # noqa

CASTING_DIRECTOR = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNva1hNOFJVX05xWExzUjRqNTlzUiJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHktc2hvcC5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWVjNGZkZmM0MWI0YWIwYzZjOTJjNGFhIiwiYXVkIjpbImFnZW5jeSIsImh0dHBzOi8vdWRhY2l0eS1zaG9wLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE1ODk5ODY1NzEsImV4cCI6MTU5MDA3Mjk3MSwiYXpwIjoiZUg5QXBvRVZsaVliZ3pOWlVWN2ZnNXNOc3dwZDdxcXMiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvcnMiXX0.Vs4Uu6ADbqWJawK-8gb--IbDFyWAiBaWPWcF4VDykgmW1bYgx5XcHgPcUqHNrpp5RS8O9aHXugRTWb9qT0jSsnES7yAHFZ-N0Jspgn9UTgdkiXeMA3M7aWfgxsNll_yTWwN980yqQ0SFFSwM3qRxmpWGRKLsAFpHHzc6ZxeSld9FA2vZz3q5b8ln3izm-y2zJeaJJhMY4xg8JN9YEd8TZmhhbwDe1UwjW0pF7l0NgzmIMvNxRUKwppqETwXm0grSwTo-lMyPU5iWoQxaSna_vxO_8NNC7H_sX0tWxisQLV3vQcAgMwwH6Amwcbp4IGPzsrcQpoaH1kx3EI7c3ikzqA')  # noqa
EXECUTIVE_PRODUCER = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkNva1hNOFJVX05xWExzUjRqNTlzUiJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHktc2hvcC5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NWVjNGZlM2Y0MWI0YWIwYzZjOTJjNWFhIiwiYXVkIjpbImFnZW5jeSIsImh0dHBzOi8vdWRhY2l0eS1zaG9wLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE1ODk5ODY2MTIsImV4cCI6MTU5MDA3MzAxMiwiYXpwIjoiZUg5QXBvRVZsaVliZ3pOWlVWN2ZnNXNOc3dwZDdxcXMiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmFjdG9ycyIsImRlbGV0ZTptb3ZpZXMiLCJnZXQ6YWN0b3JzIiwiZ2V0Om1vdmllcyIsInBhdGNoOmFjdG9ycyIsInBhdGNoOm1vdmllcyIsInBvc3Q6YWN0b3JzIiwicG9zdDptb3ZpZXMiXX0.GZRyOQjtvcQxOZq5SwmIKznqTt5IgoFVexoLYQpKBtyukpAYyTnOFkzVPE7LQ-rAMoMpIJF6tW-3zObkE7WDrRAn_eOgzopARymTlQcHgVoF0F1hupUjqLcfjgwv3bgla7cbLqqEIz1IYT1JU-TeNaMl2B50YZ_el2eXncu4Gd5nE1iUptzjyKY5x2lPLrY9LN-apSxdg5yA9Wc44WfDD-kwRUTTISJzrxvbzdO3DUnw87JvqE6F74XI_dtpeFEmq425IPTZTg6DM_KaiFz6k0PHS328R5BME4rn9dj36S6PB5EDegVegyjKXGKV5PZT-RSIea7aI9Mn133ZYkTNbw')  # noqa


class CastingAgencyTest(unittest.TestCase):
    """Setup test suite for the routes"""

    def setUp(self):
        """Setup application """
        self.app = create_app()
        self.client = self.app.test_client
        self.test_movie = {
            'title': 'Kungfu Masters',
            'release_date': '2020-05-06',
        }
        self.database_path = os.environ['DATABASE_URL']

        setup_db(self.app, self.database_path)

    def tearDown(self):
        """Executed after each test"""
        pass

    #  Tests that you can get all movies
    def test_get_all_movies(self):
        response = self.client().get(
            '/movies',
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])

    # Test to get a specific movie
    def test_get_movie_by_id(self):
        response = self.client().get(
            '/movies/1',
            headers={"Authorization": "Bearer " + CASTING_ASSISTANT}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['title'], 'Terminator Dark Fate')

    # tests for an invalid id to get a specific movie
    def test_404_get_movie_by_id(self):
        response = self.client().get(
            '/movies/100',
            headers={"Authorization": "Bearer " + CASTING_ASSISTANT}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    # Test to create a movie
    def test_post_movie(self):
        response = self.client().post(
            '/movies',
            json=self.test_movie,
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['title'], 'Kungfu Masters')
        self.assertEqual(
            data['movie']['release_date'],
            'Wed, 06 May 2020 00:00:00 GMT'
        )

    # Test to create a movie if no data is sent
    def test_400_post_movie(self):
        response = self.client().post(
            '/movies',
            json={},
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    # tests RBAC for creating a movie
    def test_401_post_movie_unauthorized(self):
        response = self.client().post(
            '/movies',
            json=self.test_movie,
            headers={'Authorization': f'Bearer {CASTING_DIRECTOR}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found.')

    # Test to Update a movie
    def test_patch_movie(self):
        response = self.client().patch(
            '/movies/1',
            json={'title': 'Revelations', 'release_date': "2019-11-12"},
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])
        self.assertEqual(data['movie']['title'], 'Revelations')
        self.assertEqual(
            data['movie']['release_date'],
            'Tue, 12 Nov 2019 00:00:00 GMT'
        )

    # Test that 400 is returned if no data is sent to update a movie
    def test_400_patch_movie(self):
        response = self.client().patch(
            '/movies/1',
            json={},
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    # tests RBAC for updating a movie
    def test_401_patch_movie_unauthorized(self):
        response = self.client().patch(
            '/movies/1',
            json=self.test_movie,
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found.')

    # tests that 404 is returned for an invalid id to get a specific movie
    def test_404_patch_movie(self):
        response = self.client().patch(
            '/movies/12323',
            json=self.test_movie,
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    # tests to delete a movie
    def test_delete_movie(self):
        response = self.client().delete(
            '/movies/2',
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['message'])

    # tests RBAC for deleting a movie
    def test_401_delete_movie(self):
        response = self.client().delete(
            '/movies/2',
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found.')

    # tests for an invalid id to delete a specific movie
    def test_404_delete_movie(self):
        response = self.client().delete(
            '/movies/22321',
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    #  Tests that you can get all actors
    def test_get_all_actors(self):
        response = self.client().get(
            '/actors',
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])

    # Test to get a specific actor
    def test_get_actor_by_id(self):
        response = self.client().get(
            '/actors/1',
            headers={"Authorization": "Bearer " + CASTING_ASSISTANT}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor'])
        self.assertEqual(data['actor']['name'], 'Will Smith')

    # tests for an invalid id to get a specific actor
    def test_404_get_actor_by_id(self):
        response = self.client().get(
            '/actors/100',
            headers={"Authorization": "Bearer " + CASTING_ASSISTANT}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    # Test to create an actor
    def test_post_actor(self):
        response = self.client().post(
            '/actors',
            json={'name': 'Karl', 'age': 20, "gender": "male"},
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['name'], 'Karl')
        self.assertEqual(data['actor']['age'], 20)
        self.assertEqual(data['actor']['gender'], 'male')

    # Test to create an actor if no data is sent
    def test_400_post_actor(self):
        response = self.client().post(
            '/actors',
            json={},
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    # tests RBAC for creating an actor
    def test_401_post_actor_unauthorized(self):
        response = self.client().post(
            '/actors',
            json={'name': 'Mary', 'age': 22, "gender": "female"},
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found.')

    # Test to Update an actor
    def test_patch_actor(self):
        response = self.client().patch(
            '/actors/1',
            json={'name': 'Mariam', 'age': 25, "gender": "female"},
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['actor']['name'], 'Mariam')
        self.assertEqual(data['actor']['age'], 25)
        self.assertEqual(data['actor']['gender'], 'female')

    # Test that 400 is returned if no data is sent to update an actor
    def test_400_patch_actor(self):
        response = self.client().patch(
            '/actors/1',
            json={},
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 400)
        self.assertEqual(data['message'], 'bad request')

    # tests RBAC for updating an actor
    def test_401_patch_actor_unauthorized(self):
        response = self.client().patch(
            '/actors/1',
            json={'name': 'John', 'age': 25, "gender": "male"},
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found.')

    # tests that 404 is returned for an invalid id to get a specific actor
    def test_404_patch_actor(self):
        response = self.client().patch(
            '/actor/12323',
            json={'name': 'Johnathan', 'age': 25, "gender": "male"},
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')

    # tests to delete an actor
    def test_delete_actor(self):
        response = self.client().delete(
            '/actors/2',
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['message'])

    # tests RBAC for deleting an actor
    def test_401_delete_actor(self):
        response = self.client().delete(
            '/actors/2',
            headers={'Authorization': f'Bearer {CASTING_ASSISTANT}'}
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['code'], 'unauthorized')
        self.assertEqual(data['description'], 'Permission not found.')

    # tests for an invalid id to get a specific actor
    def test_404_delete_actor(self):
        response = self.client().delete(
            '/actors/22321',
            headers={'Authorization': f'Bearer {EXECUTIVE_PRODUCER}'}
        )
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['error'], 404)
        self.assertEqual(data['message'], 'resource not found')


# Make the tests executable
if __name__ == "__main__":
    unittest.main()
