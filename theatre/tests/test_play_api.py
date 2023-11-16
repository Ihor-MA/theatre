from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from theatre.models import Play, Genre, Actor
from theatre.seriazilers import PlayListSerializer, PlayDetailSerializer

PLAY_URL = reverse("theatre:play-list")


def play_detail_url(play_id: int):
    return reverse("theatre:play-detail", args=[play_id])


def sample_play(**params):
    defaults = {
        "title": "Sample play",
        "description": "Sample description",
    }
    defaults.update(params)

    return Play.objects.create(**defaults)


def sample_genre(**params):
    defaults = {
        "name": "Drama",
    }
    defaults.update(params)

    return Genre.objects.create(**defaults)


def sample_actor(**params):
    defaults = {"first_name": "George", "last_name": "Clooney"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


class UnauthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedPlayApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass",
        )
        self.client.force_authenticate(self.user)

    def test_list_plays(self):
        play_with_genres = sample_play()
        play_with_actors = sample_play()

        genre = sample_genre()
        play_with_genres.genres.add(genre)

        actor = sample_actor()
        play_with_actors.actors.add(actor)

        res = self.client.get(PLAY_URL)

        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_plays_by_actors(self):
        play1 = sample_play(title="play1")
        play2 = sample_play(title="play2")

        actor1 = sample_actor(first_name="John", last_name="Cena")
        actor2 = sample_actor(first_name="John", last_name="Wick")

        play1.actors.add(actor1)
        play2.actors.add(actor2)

        play3 = sample_play(title="without actors")

        res = self.client.get(PLAY_URL, {"actors": f"{actor1.id}, {actor2.id}"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_plays_by_genres(self):
        play1 = sample_play(title="play1")
        play2 = sample_play(title="play2")

        genre1 = sample_genre(name="Fantasy")
        genre2 = sample_genre(name="Horror")

        play1.genres.add(genre1)
        play2.genres.add(genre2)

        play3 = sample_play(title="without genres")

        res = self.client.get(PLAY_URL, {"genres": f"{genre1.id}, {genre2.id}"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)
        serializer3 = PlayListSerializer(play3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_plays_by_title(self):
        play1 = sample_play(title="play1")
        play2 = sample_play(title="play2")

        res = self.client.get(PLAY_URL,  {"title": f"{play1.title}"})

        serializer1 = PlayListSerializer(play1)
        serializer2 = PlayListSerializer(play2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_play_detail(self):
        play = sample_play()
        play.genres.add(sample_genre())
        play.actors.add(sample_actor())

        url = play_detail_url(play.id)
        res = self.client.get(url)

        serializer = PlayDetailSerializer(play)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_movie_forbidden(self):
        payload = {
            "title": "Sample play",
            "description": "Sample description",
        }

        res = self.client.post(PLAY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminPlayAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com",
            "testpass",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    # def test_create_play(self):
    #     payload = {
    #         "title": "Sample play",
    #         "description": "Sample description",
    #     }
    #
    #     res = self.client.post(PLAY_URL, payload)
    #     play = Play.objects.get(id=res.data["id"])
    #
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     for key in payload:
    #         self.assertEqual(payload[key], getattr(play, key))

    # def test_create_play_with_genres(self):
    #     genre1 = sample_genre(name="Fantasy")
    #     genre2 = sample_genre(name="Horror")
    #
    #     payload = {
    #         "title": "Sample play",
    #         "description": "Sample description",
    #         "genres": [genre1.id, genre2.id]
    #     }
    #
    #     res = self.client.post(PLAY_URL, payload)
    #     play = Play.objects.get(id=res.data["id"])
    #     genres = play.genres.all()
    #
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #
    #     self.assertEqual(genres.count(), 2)
    #     self.assertIn(genre1, genres)
    #     self.assertIn(genre2, genres)

    # def test_create_movie_with_actors(self):
    #     actor1 = sample_actor(first_name="John", last_name="Cena")
    #     actor2 = sample_actor(first_name="John", last_name="Wick")
    #
    #     payload = {
    #         "title": "Sample movie",
    #         "description": "Sample description",
    #         "actors": [actor1.id, actor2.id]
    #     }
    #
    #     res = self.client.post(PLAY_URL, payload)
    #     play = Play.objects.get(id=res.data["id"])
    #     actors = play.actors.all()
    #
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #
    #     self.assertEqual(actors.count(), 2)
    #     self.assertIn(actor1, actors)
    #     self.assertIn(actor2, actors)

    def test_delete_or_put_movie_not_allowed(self):
        play = sample_play()
        url = play_detail_url(play.id)

        res_delete = self.client.delete(url)
        res_put = self.client.put(url)

        self.assertEqual(res_delete.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(res_put.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
