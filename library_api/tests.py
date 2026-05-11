from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from rest_framework.test import APIClient
from rest_framework import status

from .models import (
    Author,
    AuthorProfile,
    Book,
    BorrowRecord,
    Category,
    Patron,
    PatronProfile,
    User,
)


class ModelTests(TestCase):
    def test_create_patron_user(self):
        user = User.objects.create_user(
            email="patron@test.com", first_name="Pat", password="testpass123"
        )
        self.assertEqual(user.role, User.Role.PATRON)
        self.assertTrue(user.check_password("testpass123"))

    def test_create_author_user(self):
        user = User.objects.create_user(
            email="author@test.com",
            first_name="Auth",
            password="testpass123",
            role=User.Role.AUTHOR,
        )
        self.assertEqual(user.role, User.Role.AUTHOR)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@test.com", first_name="Admin", password="testpass123"
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_author_proxy(self):
        user = User.objects.create_user(
            email="a@test.com",
            first_name="A",
            password="p",
            role=User.Role.AUTHOR,
        )
        author = Author.objects.get(pk=user.pk)
        self.assertEqual(author.role, User.Role.AUTHOR)

    def test_patron_proxy(self):
        user = User.objects.create_user(
            email="p@test.com", first_name="P", password="p"
        )
        patron = Patron.objects.get(pk=user.pk)
        self.assertEqual(patron.role, User.Role.PATRON)

    def test_category_creation(self):
        cat = Category.objects.create(name="Fiction")
        self.assertEqual(cat.name, "Fiction")

    def test_book_creation(self):
        author_user = User.objects.create_user(
            email="a@t.com", first_name="A", password="p", role=User.Role.AUTHOR
        )
        author_profile = AuthorProfile.objects.get(user=author_user)
        cat = Category.objects.create(name="Sci-Fi")
        book = Book.objects.create(
            isbn="978-3-16-148410-0",
            name="Test Book",
            year_published="2024-01-01",
            stock_copies=5,
        )
        book.authors.add(author_profile)
        book.category.add(cat)
        self.assertEqual(book.name, "Test Book")
        self.assertEqual(book.stock_copies, 5)

    def test_borrow_record_overdue(self):
        author_user = User.objects.create_user(
            email="a@t.com", first_name="A", password="p", role=User.Role.AUTHOR
        )
        author_profile = AuthorProfile.objects.get(user=author_user)
        patron_user = User.objects.create_user(
            email="p@t.com", first_name="P", password="p"
        )
        patron_profile = PatronProfile.objects.get(user=patron_user)
        book = Book.objects.create(
            isbn="1", name="B", year_published="2024-01-01", stock_copies=1
        )
        book.authors.add(author_profile)
        record = BorrowRecord.objects.create(
            book=book,
            patron=patron_profile,
            due_date=date.today() - timedelta(days=1),
        )
        self.assertTrue(record.is_overdue)

    def test_borrow_record_not_overdue(self):
        patron_user = User.objects.create_user(
            email="p@t.com", first_name="P", password="p"
        )
        patron_profile = PatronProfile.objects.get(user=patron_user)
        book = Book.objects.create(
            isbn="2", name="B2", year_published="2024-01-01", stock_copies=1
        )
        record = BorrowRecord.objects.create(
            book=book,
            patron=patron_profile,
            due_date=date.today() + timedelta(days=5),
        )
        self.assertFalse(record.is_overdue)

    def test_borrow_record_returned_not_overdue(self):
        patron_user = User.objects.create_user(
            email="p@t.com", first_name="P", password="p"
        )
        patron_profile = PatronProfile.objects.get(user=patron_user)
        book = Book.objects.create(
            isbn="3", name="B3", year_published="2024-01-01", stock_copies=1
        )
        record = BorrowRecord.objects.create(
            book=book,
            patron=patron_profile,
            due_date=date.today() - timedelta(days=1),
            returned_at=now(),
        )
        self.assertFalse(record.is_overdue)


class SignalTests(TestCase):
    def test_author_profile_created(self):
        user = User.objects.create_user(
            email="a@t.com", first_name="A", password="p", role=User.Role.AUTHOR
        )
        self.assertTrue(AuthorProfile.objects.filter(user=user).exists())

    def test_patron_profile_created(self):
        user = User.objects.create_user(
            email="p@t.com", first_name="P", password="p"
        )
        self.assertTrue(PatronProfile.objects.filter(user=user).exists())

    def test_profile_deleted_on_user_delete(self):
        user = User.objects.create_user(
            email="p@t.com", first_name="P", password="p"
        )
        profile_id = PatronProfile.objects.get(user=user).id
        user.delete()
        self.assertFalse(PatronProfile.objects.filter(id=profile_id).exists())


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse("library_api:signup")
        self.login_url = reverse("library_api:login")
        self.user_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@test.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }

    def test_signup_success(self):
        resp = self.client.post(self.signup_url, self.user_data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

    def test_signup_password_mismatch(self):
        data = {**self.user_data, "password2": "DifferentPass1!"}
        resp = self.client.post(self.signup_url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        self.client.post(self.signup_url, self.user_data, format="json")
        resp = self.client.post(
            self.login_url,
            {"email": "john@test.com", "password": "StrongPass1!"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("token", resp.data)

    def test_login_invalid_credentials(self):
        resp = self.client.post(
            self.login_url,
            {"email": "no@test.com", "password": "wrong"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        self.client.post(self.signup_url, self.user_data, format="json")
        login_resp = self.client.post(
            self.login_url,
            {"email": "john@test.com", "password": "StrongPass1!"},
            format="json",
        )
        token = login_resp.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        resp = self.client.post(reverse("library_api:logout"))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_all(self):
        self.client.post(self.signup_url, self.user_data, format="json")
        login_resp = self.client.post(
            self.login_url,
            {"email": "john@test.com", "password": "StrongPass1!"},
            format="json",
        )
        token = login_resp.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        resp = self.client.post(reverse("library_api:logoutall"))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patron = User.objects.create_user(
            email="patron@test.com", first_name="Pat", password="testpass123"
        )
        self.admin = User.objects.create_superuser(
            email="admin@test.com", first_name="Admin", password="testpass123"
        )
        self.other = User.objects.create_user(
            email="other@test.com", first_name="Other", password="testpass123"
        )

    def test_list_users_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(reverse("library_api:users"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_list_users_unauthorized(self):
        resp = self.client.get(reverse("library_api:users"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_users_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.get(reverse("library_api:users"))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.get(
            reverse("library_api:user", kwargs={"id": self.patron.id})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["email"], "patron@test.com")

    def test_get_user_not_found(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.get(reverse("library_api:user", kwargs={"id": 999}))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own_user(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.put(
            reverse("library_api:update-user", kwargs={"id": self.patron.id}),
            {"first_name": "Updated"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.patron.refresh_from_db()
        self.assertEqual(self.patron.first_name, "Updated")

    def test_update_other_user_forbidden(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.put(
            reverse("library_api:update-user", kwargs={"id": self.other.id}),
            {"first_name": "Hacked"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_user_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.delete(
            reverse("library_api:delete-user", kwargs={"id": self.other.id})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=self.other.id).exists())

    def test_delete_user_unauthorized(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.delete(
            reverse("library_api:delete-user", kwargs={"id": self.other.id})
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_user_shows_own_data_after_update(self):
        self.client.force_authenticate(user=self.patron)
        self.client.put(
            reverse("library_api:update-user", kwargs={"id": self.patron.id}),
            {"first_name": "UpdatedPat"},
            format="json",
        )
        resp = self.client.get(
            reverse("library_api:user", kwargs={"id": self.patron.id})
        )
        self.assertEqual(resp.data["first_name"], "UpdatedPat")


class BookAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = User.objects.create_user(
            email="author@test.com",
            first_name="Auth",
            password="testpass123",
            role=User.Role.AUTHOR,
        )
        self.author_profile = AuthorProfile.objects.get(user=self.author)
        self.patron = User.objects.create_user(
            email="patron@test.com", first_name="Pat", password="testpass123"
        )
        self.cat = Category.objects.create(name="Fiction")
        self.book_data = {
            "isbn": "978-3-16-148410-0",
            "name": "Test Book",
            "year_published": "2024-01-01",
            "stock_copies": 3,
        }

    def test_create_book_as_author(self):
        self.client.force_authenticate(user=self.author)
        data = {**self.book_data, "authors": [self.author_profile.id]}
        resp = self.client.post(
            reverse("library_api:create-book"), data, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

    def test_create_book_as_patron_forbidden(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.post(
            reverse("library_api:create-book"), self.book_data, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_books(self):
        self.client.force_authenticate(user=self.patron)
        book = Book.objects.create(
            isbn="1", name="B1", year_published="2024-01-01", stock_copies=1
        )
        book.authors.add(self.author_profile)
        resp = self.client.get(reverse("library_api:list-books"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("results", resp.data)
        self.assertEqual(len(resp.data["results"]), 1)

    def test_update_own_book(self):
        self.client.force_authenticate(user=self.author)
        book = Book.objects.create(
            isbn="1", name="B1", year_published="2024-01-01", stock_copies=1
        )
        book.authors.add(self.author_profile)
        resp = self.client.patch(
            reverse("library_api:update-book", kwargs={"pk": book.isbn}),
            {"name": "Updated Book"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.name, "Updated Book")

    def test_delete_own_book(self):
        self.client.force_authenticate(user=self.author)
        book = Book.objects.create(
            isbn="1", name="B1", year_published="2024-01-01", stock_copies=1
        )
        book.authors.add(self.author_profile)
        resp = self.client.delete(
            reverse("library_api:delete-book", kwargs={"pk": book.isbn})
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    def test_search_books_by_name(self):
        self.client.force_authenticate(user=self.patron)
        b1 = Book.objects.create(
            isbn="1", name="Dragon Tales", year_published="2024-01-01", stock_copies=1
        )
        b1.authors.add(self.author_profile)
        b2 = Book.objects.create(
            isbn="2", name="Space Odyssey", year_published="2024-01-01", stock_copies=1
        )
        b2.authors.add(self.author_profile)
        resp = self.client.get(
            reverse("library_api:list-books"), {"search": "Dragon"}
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [b["name"] for b in resp.data["results"]]
        self.assertIn("Dragon Tales", titles)
        self.assertNotIn("Space Odyssey", titles)

    def test_search_books_by_isbn(self):
        self.client.force_authenticate(user=self.patron)
        b1 = Book.objects.create(
            isbn="111-111", name="B1", year_published="2024-01-01", stock_copies=1
        )
        b1.authors.add(self.author_profile)
        b2 = Book.objects.create(
            isbn="222-222", name="B2", year_published="2024-01-01", stock_copies=1
        )
        b2.authors.add(self.author_profile)
        resp = self.client.get(
            reverse("library_api:list-books"), {"search": "111"}
        )
        isbns = [b["isbn"] for b in resp.data["results"]]
        self.assertIn("111-111", isbns)
        self.assertNotIn("222-222", isbns)

    def test_delete_other_authors_book_forbidden(self):
        self.client.force_authenticate(user=self.author)
        other_author = User.objects.create_user(
            email="other_auth@test.com",
            first_name="Other",
            password="testpass123",
            role=User.Role.AUTHOR,
        )
        other_profile = AuthorProfile.objects.get(user=other_author)
        book = Book.objects.create(
            isbn="1", name="B1", year_published="2024-01-01", stock_copies=1
        )
        book.authors.add(other_profile)
        resp = self.client.delete(
            reverse("library_api:delete-book", kwargs={"pk": book.isbn})
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthorized_access_to_books(self):
        resp = self.client.get(reverse("library_api:list-books"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class CategoryAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@test.com", first_name="Admin", password="testpass123"
        )
        self.patron = User.objects.create_user(
            email="patron@test.com", first_name="Pat", password="testpass123"
        )

    def test_list_categories(self):
        Category.objects.create(name="Fiction")
        Category.objects.create(name="Non-Fiction")
        self.client.force_authenticate(user=self.patron)
        resp = self.client.get(reverse("library_api:list-category"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 2)

    def test_create_category_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.post(
            reverse("library_api:create-category"),
            {"name": "Sci-Fi"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 1)

    def test_create_category_as_non_admin_forbidden(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.post(
            reverse("library_api:create-category"),
            {"name": "Sci-Fi"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category(self):
        self.client.force_authenticate(user=self.admin)
        cat = Category.objects.create(name="Old")
        resp = self.client.put(
            reverse("library_api:update-categoryk", kwargs={"pk": cat.id}),
            {"name": "New"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        cat.refresh_from_db()
        self.assertEqual(cat.name, "New")

    def test_delete_category(self):
        self.client.force_authenticate(user=self.admin)
        cat = Category.objects.create(name="Temp")
        resp = self.client.delete(
            reverse("library_api:delete-category", kwargs={"pk": cat.id})
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)


class BorrowReturnTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = User.objects.create_user(
            email="author@test.com",
            first_name="Auth",
            password="testpass123",
            role=User.Role.AUTHOR,
        )
        self.author_profile = AuthorProfile.objects.get(user=self.author)
        self.patron = User.objects.create_user(
            email="patron@test.com", first_name="Pat", password="testpass123"
        )
        self.patron_profile = PatronProfile.objects.get(user=self.patron)
        self.book = Book.objects.create(
            isbn="978-3-16-148410-0",
            name="Test Book",
            year_published="2024-01-01",
            stock_copies=2,
        )
        self.book.authors.add(self.author_profile)

    def test_borrow_book_success(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.post(
            reverse("library_api:borrow-book", kwargs={"pk": self.book.isbn})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_copies, 1)
        self.assertIn(self.patron_profile, self.book.borrowed_by.all())
        self.assertTrue(
            BorrowRecord.objects.filter(
                book=self.book, patron=self.patron_profile, returned_at__isnull=True
            ).exists()
        )

    def test_borrow_book_creates_borrow_record_with_due_date(self):
        self.client.force_authenticate(user=self.patron)
        self.client.post(
            reverse("library_api:borrow-book", kwargs={"pk": self.book.isbn})
        )
        record = BorrowRecord.objects.get(
            book=self.book, patron=self.patron_profile
        )
        self.assertEqual(record.due_date, date.today() + timedelta(days=14))
        self.assertIsNone(record.returned_at)

    def test_borrow_book_already_borrowed(self):
        self.client.force_authenticate(user=self.patron)
        self.book.borrowed_by.add(self.patron_profile)
        self.book.stock_copies = 1
        self.book.save()
        resp = self.client.post(
            reverse("library_api:borrow-book", kwargs={"pk": self.book.isbn})
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_borrow_book_no_stock(self):
        self.client.force_authenticate(user=self.patron)
        self.book.stock_copies = 0
        self.book.save()
        resp = self.client.post(
            reverse("library_api:borrow-book", kwargs={"pk": self.book.isbn})
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_borrow_book_not_found(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.post(
            reverse("library_api:borrow-book", kwargs={"pk": "invalid-isbn"})
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_book_success(self):
        self.client.force_authenticate(user=self.patron)
        self.book.borrowed_by.add(self.patron_profile)
        self.book.stock_copies = 1
        self.book.save()
        BorrowRecord.objects.create(
            book=self.book,
            patron=self.patron_profile,
            due_date=date.today() + timedelta(days=10),
        )
        resp = self.client.post(
            reverse("library_api:return-book", kwargs={"pk": self.book.isbn})
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_copies, 2)
        self.assertNotIn(self.patron_profile, self.book.borrowed_by.all())

    def test_return_book_marks_returned_at(self):
        self.client.force_authenticate(user=self.patron)
        self.book.borrowed_by.add(self.patron_profile)
        self.book.stock_copies = 1
        self.book.save()
        record = BorrowRecord.objects.create(
            book=self.book,
            patron=self.patron_profile,
            due_date=date.today() + timedelta(days=10),
        )
        self.client.post(
            reverse("library_api:return-book", kwargs={"pk": self.book.isbn})
        )
        record.refresh_from_db()
        self.assertIsNotNone(record.returned_at)

    def test_return_book_not_borrowed(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.post(
            reverse("library_api:return-book", kwargs={"pk": self.book.isbn})
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_book_not_found(self):
        self.client.force_authenticate(user=self.patron)
        resp = self.client.post(
            reverse("library_api:return-book", kwargs={"pk": "invalid-isbn"})
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_author_cannot_borrow(self):
        self.client.force_authenticate(user=self.author)
        resp = self.client.post(
            reverse("library_api:borrow-book", kwargs={"pk": self.book.isbn})
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_borrow_updates_stock_correctly(self):
        self.client.force_authenticate(user=self.patron)
        self.client.post(
            reverse("library_api:borrow-book", kwargs={"pk": self.book.isbn})
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_copies, 1)
        self.client.post(
            reverse("library_api:return-book", kwargs={"pk": self.book.isbn})
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock_copies, 2)
