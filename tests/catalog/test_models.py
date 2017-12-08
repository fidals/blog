"""Defines tests for models in Catalog app."""
from django.test import TestCase

from pages.models import CustomPage

from tests.catalog.models import MockCategory, MockProduct, MockCategoryWithDefaultPage


class TestCategoryTree(TestCase):
    """Test suite for category operations"""

    def setUp(self):
        """
        Defines testing data.
        Two categories: Root and Child (of root).
        Two products: popular and unpopular (both from Child category)
        """

        self.test_root_category = MockCategory.objects.get_or_create(
            name='Test root'
        )[0]

        self.test_child_of_root_category = MockCategory.objects.get_or_create(
            name='Test child',
            parent=self.test_root_category
        )[0]

        self.test_child_of_ancestor_category = MockCategory.objects.get_or_create(
            name='Test descendants',
            parent=self.test_child_of_root_category
        )[0]

        self.test_unpopular_product = MockProduct.objects.get_or_create(
            name='Unpopular',
            price=10,
            category=self.test_child_of_root_category,
            in_stock=10
        )[0]

        self.test_popular_product = MockProduct.objects.get_or_create(
            name='Popular',
            price=20,
            category=self.test_child_of_ancestor_category,
            in_stock=10,
            is_popular=True,
        )[0]

    def test_root_categories(self):
        """There should be only one root category."""

        roots = MockCategory.objects.root_nodes()
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].name, self.test_root_category.name)

    def test_children_of_root(self):
        """Should be one direct child of root category."""

        roots = MockCategory.objects.root_nodes()[0]
        children = roots.get_children()
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].name, self.test_child_of_root_category.name)

    def test_root_has_no_products(self):
        """Root category shouldn't have any products."""

        roots = MockCategory.objects.root_nodes()[0]
        products = roots.products.all()
        self.assertFalse(products.exists())


class CategoryToPageRelationTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_tree_page, _ = CustomPage.objects.get_or_create(slug='catalog')
        cls.root_category = MockCategoryWithDefaultPage.objects.create(
            name='All batteries',
        )
        cls.root_category.page.slug = 'all'
        cls.root_category.page.save()
        cls.page_type = cls.root_category.related_model_name

    def __create_category(self, slug, page=None):
        category = MockCategoryWithDefaultPage.objects.create(
            name='Battery {}'.format(slug),
            page=page,
            parent=self.root_category
        )
        category.page.slug = slug
        category.page.save()
        return category

    def test_category_create_related_page(self):
        """
        MockCategoryWithDefaultPage without related page should create and return related page
        by MockCategoryWithDefaultPage.save() call
        """
        category = self.__create_category(slug='first')
        self.assertTrue('category' in category.page.related_model_name)
        self.assertEqual(category.url, category.page.url)
        self.assertEqual(category.page.model, category)

    def test_category_tree_page_parent(self):
        """
        MockCategoryWithDefaultPage tree page should be auto-created as page parent
        for every root MockCategoryWithDefaultPage. In other words:
        MockCategoryWithDefaultPage.page.parent == category_tree_page
        """
        slug = 'fifth'
        category = MockCategoryWithDefaultPage.objects.create(
            name='Battery {}'.format(slug), parent=None)
        category.page.slug = slug
        category.page.save()
        self.assertEqual(category.page.parent, self.category_tree_page)

    def test_category_create_page_for_sync_tree(self):
        """
        MockCategoryWithDefaultPage should bind parent for it's page if parent doesn't exist
        """
        category = self.__create_category(slug='sixth')
        self.assertEqual(category.parent.page, category.page.parent)
        self.assertEqual(category.parent.page.slug, category.page.parent.slug)

    def test_category_return_page_by_sync_tree(self):
        """
        If MockCategoryWithDefaultPage page have parent,
        MockCategoryWithDefaultPage save() hook should do nothing
        """
        category = self.__create_category(slug='seventh')
        category.page.parent = self.root_category.page
        category.page.save()
        category.save()  # category.save() hooks sync_tree() method
        self.assertEqual(category.page.parent, self.root_category.page)


class TestProductToPageRelation(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root_category = MockCategory.objects.create(
            name='All batteries',
        )
        cls.root_category.page.slug = 'all'
        cls.root_category.page.save()
        cls.page_type = 'catalog_product'

    @classmethod
    def create_product(self, slug, page=None):
        return MockProduct.objects.create(
            name=slug,
            page=page,
            category=self.root_category,
            price=123
        )

    @property
    def category_tree_page(self):
        return CustomPage.objects.get(slug='category_tree')

    def test_product_create_related_page(self):
        """
        MockProduct without related page should create and return related page
        by product.save() call
        """
        product = self.create_product(slug='first')
        self.assertEqual(product.related_model_name, product.page.related_model_name)
        self.assertTrue(product.page.model, product)

    def test_category_create_page_for_sync_tree(self):
        """
        MockProduct should bind parent for it's page if parent doesn't exist
        """
        product = self.create_product(slug='sixth')
        category = product.category
        self.assertEqual(category, product.parent)
        self.assertEqual(category.page, product.page.parent)
        self.assertEqual(category.page.slug, product.page.parent.slug)

    def test_product_return_page_by_sync_tree(self):
        """
        If product page have parent, category sync tree should do nothing
        """
        product = self.create_product(slug='seventh')
        product.page.parent = self.root_category.page
        product.page.save()
        product.save()  # category.save() hooks tree sync
        self.assertEqual(product.page.parent, self.root_category.page)


class TestProduct(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category_id = 1
        cls.category = MockCategory.objects.create(name='some category', id=cls.category_id)

        cls.test_popular_product = MockProduct.objects.create(
            name="Popular",
            price=20,
            category=cls.category,
            in_stock=10,
            is_popular=True,
        )
        MockProduct.objects.create(
            name="unpopular #1",
            price=20,
            category=cls.category,
            in_stock=10,
            is_popular=False,
        )
        MockProduct.objects.create(
            name="unpopular #2",
            price=20,
            category=MockCategory.objects.create(name='another category', id=777),
            in_stock=10,
            is_popular=False,
        )


    def test_popular_products(self):
        """Should be one popular product."""
        popular = MockProduct.objects.filter(is_popular=True)

        self.assertEqual(len(popular), 1)
        self.assertEqual(popular[0].name, self.test_popular_product.name)

    def test_get_product_by_category(self):
        """We can get products related to category by category_id or Category instance"""
        products_by_instance = MockProduct.objects.get_by_category(self.category)

        self.assertEqual(products_by_instance.count(), 2)

        for products_by_instance in products_by_instance:
            self.assertEqual(products_by_instance.category, self.category)

    def test_get_offset(self):
        products_offset = MockProduct.objects.all().get_offset(1, 3)

        self.assertEqual(len(products_offset), 2)