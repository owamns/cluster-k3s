import random
from uuid import uuid4
from locust import HttpUser, task, between, TaskSet
from faker import Faker
from src.config import BACKEND_BASE_URL

fake = Faker()


class UserBehavior(TaskSet):

    def on_start(self):
        self.session_id = str(uuid4())
        self.valid_product_ids = []
        self.valid_category_ids = []
        print(f"Nuevo usuario iniciado con session_id: {self.session_id}")
        self._fetch_valid_ids()

    def _fetch_valid_ids(self):
        response = self.client.get("/api/categories/", name="/api/categories")
        if response.status_code == 200:
            categories = response.json()
            self.valid_category_ids = [cat['id'] for cat in categories if 'id' in cat]

        response = self.client.get("/api/products/?page=1&limit=50", name="/api/products?page&limit&category_id&search")
        if response.status_code == 200:
            products = response.json().get('data', [])
            self.valid_product_ids = [prod['id'] for prod in products if 'id' in prod]

    @task(40)
    def browse_products(self):
        self.client.get("/api/categories/", name="/api/categories")

        page = random.randint(1, 5)
        limit = random.randint(10, 20)
        category_id = random.choice(
            self.valid_category_ids) if self.valid_category_ids and random.random() > 0.5 else None
        search = fake.word()[:10] if random.random() > 0.3 else None
        params = {"page": page, "limit": limit}
        if category_id:
            params["category_id"] = category_id
        if search:
            params["search"] = search

        response = self.client.get(
            "/api/products/",
            params=params,
            name="/api/products?page&limit&category_id&search"
        )
        if response.status_code != 200:
            print(f"Error en browse_products: {response.text}")

        if self.valid_product_ids:
            product_id = random.choice(self.valid_product_ids)
            response = self.client.get(f"/api/products/{product_id}", name="/api/products/[id]")
            if response.status_code != 200:
                print(f"Error en get_product: {response.text}")

    @task(25)
    def manage_cart(self):
        if not self.valid_product_ids:
            self._fetch_valid_ids()
            if not self.valid_product_ids:
                return

        product_id = random.choice(self.valid_product_ids)
        quantity = random.randint(1, 3)
        item_id = product_id

        response = self.client.post(
            f"/api/cart/{self.session_id}/items",
            json={"product_id": product_id, "quantity": quantity},
            name="/api/cart/[session_id]/items [POST]"
        )
        if response.status_code != 201:
            print(f"Error al añadir al carrito: {response.text}")

        if random.random() > 0.5:
            response = self.client.put(
                f"/api/cart/{self.session_id}/items/{item_id}",
                json={"quantity": random.randint(1, 5)},
                name="/api/cart/[session_id]/items/[item_id] [PUT]"
            )
            if response.status_code != 200:
                print(f"Error al actualizar ítem en el carrito: {response.text}")

        if random.random() > 0.3:
            response = self.client.delete(
                f"/api/cart/{self.session_id}/items/{item_id}",
                name="/api/cart/[session_id]/items/[item_id] [DELETE]"
            )
            if response.status_code != 200:
                print(f"Error al eliminar ítem del carrito: {response.text}")

        response = self.client.get(f"/api/cart/{self.session_id}", name="/api/cart/[session_id]")
        if response.status_code != 200:
            print(f"Error al obtener carrito: {response.text}")

    @task(20)
    def checkout(self):
        if not self.valid_product_ids:
            self._fetch_valid_ids()
            if not self.valid_product_ids:
                return

        cart_filled = False
        for _ in range(random.randint(1, 3)):
            product_id = random.choice(self.valid_product_ids)
            response = self.client.post(
                f"/api/cart/{self.session_id}/items",
                json={"product_id": product_id, "quantity": 1},
                name="/api/cart/[session_id]/items [POST] (Checkout)"
            )
            if response.status_code == 201:
                cart_filled = True
            else:
                print(f"Error al añadir al carrito (Checkout): {response.text}")

        if not cart_filled:
            print(f"Carrito no se llenó correctamente para session_id: {self.session_id}")
            return

        response = self.client.get(f"/api/cart/{self.session_id}", name="/api/cart/[session_id]")
        if response.status_code == 200 and response.json():
            print(f"Carrito antes de crear pedido: {response.json()}")
            response = self.client.post(
                "/api/orders/",
                json={"session_id": self.session_id},
                name="/api/orders/ [POST]"
            )
            if response.status_code != 201:
                print(f"Error al crear pedido: {response.text}")
            else:
                order_id = response.json().get('id')
                if order_id and random.random() > 0.5:
                    response = self.client.get(f"/api/orders/{order_id}", name="/api/orders/[id]")
                    if response.status_code != 200:
                        print(f"Error al obtener pedido: {response.text}")
        else:
            print(f"Carrito vacío o error al verificar carrito: {response.text}")

        self.session_id = str(uuid4())


class StressTests(TaskSet):

    def on_start(self):
        self.session_id = str(uuid4())
        self.valid_product_ids = []
        self.valid_category_ids = []
        self._fetch_valid_ids()

    def _fetch_valid_ids(self):
        response = self.client.get("/api/products/?page=1&limit=50", name="/api/products?page&limit&category_id&search")
        if response.status_code == 200:
            products = response.json().get('data', [])
            self.valid_product_ids = [prod['id'] for prod in products if 'id' in prod]

        response = self.client.get("/api/categories/", name="/api/categories")
        if response.status_code == 200:
            categories = response.json()
            self.valid_category_ids = [cat['id'] for cat in categories if 'id' in cat]

    @task(2)
    def stress_heavy_listing(self):
        page = random.randint(1, 20)
        limit = random.randint(50, 100)
        category_id = random.choice(
            self.valid_category_ids) if self.valid_category_ids and random.random() > 0.5 else None
        search = fake.word()[:10] if random.random() > 0.3 else None
        params = {"page": page, "limit": limit}
        if category_id:
            params["category_id"] = category_id
        if search:
            params["search"] = search

        response = self.client.get(
            "/api/stress/heavy_product_listing",
            params=params,
            name="/api/stress/heavy_product_listing"
        )
        if response.status_code != 200:
            print(f"Error en heavy_product_listing: {response.text}")

    @task(1)
    def stress_concurrent_cart(self):
        if not self.valid_product_ids:
            self._fetch_valid_ids()
            if not self.valid_product_ids:
                return

        product_id = random.choice(self.valid_product_ids)
        quantity = random.randint(1, 3)
        response = self.client.post(
            f"/api/stress/concurrent_cart_additions/{self.session_id}",
            json={"product_id": product_id, "quantity": quantity},
            name="/api/stress/concurrent_cart_additions"
        )
        if response.status_code != 201:
            print(f"Error en concurrent_cart_additions: {response.text}")

    @task(1)
    def stress_mass_order(self):
        if not self.valid_product_ids:
            self._fetch_valid_ids()
            if not self.valid_product_ids:
                return

        cart_filled = False
        for _ in range(random.randint(1, 3)):
            product_id = random.choice(self.valid_product_ids)
            response = self.client.post(
                f"/api/cart/{self.session_id}/items",
                json={"product_id": product_id, "quantity": 1},
                name="/api/cart/[session_id]/items [POST] (Stress)"
            )
            if response.status_code == 201:
                cart_filled = True
            else:
                print(f"Error al añadir al carrito para mass_order: {response.text}")

        if not cart_filled:
            print(f"Carrito no se llenó correctamente para mass_order: {self.session_id}")
            return

        response = self.client.get(f"/api/cart/{self.session_id}", name="/api/cart/[session_id]")
        if response.status_code == 200 and response.json():
            print(f"Carrito antes de mass_order_creation: {response.json()}")
            response = self.client.post(
                f"/api/stress/mass_order_creation/{self.session_id}",
                name="/api/stress/mass_order_creation"
            )
            if response.status_code != 201:
                print(f"Error en mass_order_creation: {response.text}")
        else:
            print(f"Carrito vacío o error al verificar carrito para mass_order: {response.text}")

    @task(1)
    def stress_cache_miss(self):
        if not self.valid_product_ids:
            self._fetch_valid_ids()
            if not self.valid_product_ids:
                return

        product_id = random.choice(self.valid_product_ids)
        response = self.client.get(
            f"/api/stress/cache_miss_simulation/{product_id}",
            name="/api/stress/cache_miss_simulation"
        )
        if response.status_code != 200:
            print(f"Error en cache_miss_simulation: {response.text}")

    @task(1)
    def stress_mixed_load(self):
        num_requests = random.randint(5, 15)
        response = self.client.get(
            f"/api/stress/mixed_load_simulation/{num_requests}",
            name="/api/stress/mixed_load_simulation"
        )
        if response.status_code != 200:
            print(f"Error en mixed_load_simulation: {response.text}")


class WebsiteUser(HttpUser):
    host = BACKEND_BASE_URL
    wait_time = between(1, 5)

    tasks = {
        UserBehavior: 8,
        StressTests: 2
    }