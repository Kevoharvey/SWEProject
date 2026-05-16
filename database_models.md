# Database Models

Source schema: [`schema.sql`](./schema.sql)

## UML Class Diagram

```mermaid
classDiagram
    direction LR

    class User {
        +INT id PK
        +VARCHAR email UK
        +VARCHAR password_hash
        +VARCHAR full_name
        +ENUM role
        +TIMESTAMP created_at
    }

    class Farmer {
        +INT id PK
        +INT user_id FK UK
        +VARCHAR farm_name
        +TEXT description
        +VARCHAR address
        +DECIMAL location_lat
        +DECIMAL location_lng
        +VARCHAR phone
        +VARCHAR profile_image
        +ENUM status
        +TIMESTAMP created_at
    }

    class MarketSchedule {
        +INT id PK
        +INT farmer_id FK
        +VARCHAR market_name
        +VARCHAR market_address
        +DECIMAL market_lat
        +DECIMAL market_lng
        +ENUM day_of_week
        +TIME start_time
        +TIME end_time
    }

    class Product {
        +INT id PK
        +INT farmer_id FK
        +VARCHAR name
        +ENUM category
        +TEXT description
        +DECIMAL price
        +INT quantity
        +ENUM unit
        +DATE harvest_date
        +ENUM stock_status
        +BOOLEAN is_active
        +TIMESTAMP created_at
        +TIMESTAMP updated_at
    }

    class ProductPhoto {
        +INT id PK
        +INT product_id FK
        +VARCHAR photo_path
        +INT display_order
    }

    class ProductAvailability {
        +INT id PK
        +INT product_id FK
        +ENUM day_of_week
        +BOOLEAN is_available
        +UK product_id_day_of_week
    }

    class CartItem {
        +INT id PK
        +INT buyer_id FK
        +INT product_id FK
        +INT quantity
        +TIMESTAMP added_at
        +UK buyer_id_product_id
    }

    class Order {
        +INT id PK
        +INT buyer_id FK
        +VARCHAR market_location
        +DATE pickup_date
        +VARCHAR pickup_time_slot
        +ENUM status
        +DECIMAL total_amount
        +TEXT notes
        +TIMESTAMP created_at
        +TIMESTAMP updated_at
    }

    class OrderItem {
        +INT id PK
        +INT order_id FK
        +INT product_id FK
        +INT farmer_id FK
        +INT quantity
        +DECIMAL unit_price
        +DECIMAL subtotal
    }

    class Review {
        +INT id PK
        +INT order_id FK
        +INT buyer_id FK
        +INT farmer_id FK
        +INT rating
        +TEXT comment
        +TEXT farmer_response
        +TIMESTAMP created_at
        +TIMESTAMP responded_at
    }

    class Subscription {
        +INT id PK
        +INT buyer_id FK
        +INT farmer_id FK
        +TIMESTAMP created_at
        +UK buyer_id_farmer_id
    }

    class Notification {
        +INT id PK
        +INT user_id FK
        +VARCHAR title
        +TEXT message
        +VARCHAR link
        +BOOLEAN is_read
        +TIMESTAMP created_at
    }

    User "1" --> "0..1" Farmer : farmer profile
    Farmer "1" --> "0..*" MarketSchedule : attends
    Farmer "1" --> "0..*" Product : sells
    Product "1" --> "0..*" ProductPhoto : has
    Product "1" --> "0..7" ProductAvailability : available on
    User "1" --> "0..*" CartItem : buyer cart
    Product "1" --> "0..*" CartItem : selected in
    User "1" --> "0..*" Order : places
    Order "1" --> "0..*" OrderItem : contains
    Product "1" --> "0..*" OrderItem : ordered as
    Farmer "1" --> "0..*" OrderItem : fulfills
    Order "1" --> "0..*" Review : receives review in
    User "1" --> "0..*" Review : buyer writes
    Farmer "1" --> "0..*" Review : reviewed
    User "1" --> "0..*" Subscription : buyer follows
    Farmer "1" --> "0..*" Subscription : followed by
    User "1" --> "0..*" Notification : receives
```

## Relational Model

```mermaid
erDiagram
    USERS {
        INT id PK
        VARCHAR email UK
        VARCHAR password_hash
        VARCHAR full_name
        ENUM role
        TIMESTAMP created_at
    }

    FARMERS {
        INT id PK
        INT user_id FK,UK
        VARCHAR farm_name
        TEXT description
        VARCHAR address
        DECIMAL location_lat
        DECIMAL location_lng
        VARCHAR phone
        VARCHAR profile_image
        ENUM status
        TIMESTAMP created_at
    }

    MARKET_SCHEDULES {
        INT id PK
        INT farmer_id FK
        VARCHAR market_name
        VARCHAR market_address
        DECIMAL market_lat
        DECIMAL market_lng
        ENUM day_of_week
        TIME start_time
        TIME end_time
    }

    PRODUCTS {
        INT id PK
        INT farmer_id FK
        VARCHAR name
        ENUM category
        TEXT description
        DECIMAL price
        INT quantity
        ENUM unit
        DATE harvest_date
        ENUM stock_status
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    PRODUCT_PHOTOS {
        INT id PK
        INT product_id FK
        VARCHAR photo_path
        INT display_order
    }

    PRODUCT_AVAILABILITY {
        INT id PK
        INT product_id FK
        ENUM day_of_week
        BOOLEAN is_available
        UNIQUE product_day
    }

    CART_ITEMS {
        INT id PK
        INT buyer_id FK
        INT product_id FK
        INT quantity
        TIMESTAMP added_at
        UNIQUE buyer_product
    }

    ORDERS {
        INT id PK
        INT buyer_id FK
        VARCHAR market_location
        DATE pickup_date
        VARCHAR pickup_time_slot
        ENUM status
        DECIMAL total_amount
        TEXT notes
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    ORDER_ITEMS {
        INT id PK
        INT order_id FK
        INT product_id FK
        INT farmer_id FK
        INT quantity
        DECIMAL unit_price
        DECIMAL subtotal
    }

    REVIEWS {
        INT id PK
        INT order_id FK
        INT buyer_id FK
        INT farmer_id FK
        INT rating
        TEXT comment
        TEXT farmer_response
        TIMESTAMP created_at
        TIMESTAMP responded_at
    }

    SUBSCRIPTIONS {
        INT id PK
        INT buyer_id FK
        INT farmer_id FK
        TIMESTAMP created_at
        UNIQUE buyer_farmer
    }

    NOTIFICATIONS {
        INT id PK
        INT user_id FK
        VARCHAR title
        TEXT message
        VARCHAR link
        BOOLEAN is_read
        TIMESTAMP created_at
    }

    USERS ||--o| FARMERS : "has farmer profile"
    FARMERS ||--o{ MARKET_SCHEDULES : "has"
    FARMERS ||--o{ PRODUCTS : "lists"
    PRODUCTS ||--o{ PRODUCT_PHOTOS : "has"
    PRODUCTS ||--o{ PRODUCT_AVAILABILITY : "has weekly availability"
    USERS ||--o{ CART_ITEMS : "buyer owns"
    PRODUCTS ||--o{ CART_ITEMS : "appears in"
    USERS ||--o{ ORDERS : "buyer places"
    ORDERS ||--o{ ORDER_ITEMS : "contains"
    PRODUCTS ||--o{ ORDER_ITEMS : "sold in"
    FARMERS ||--o{ ORDER_ITEMS : "fulfills"
    ORDERS ||--o{ REVIEWS : "review source"
    USERS ||--o{ REVIEWS : "buyer writes"
    FARMERS ||--o{ REVIEWS : "receives"
    USERS ||--o{ SUBSCRIPTIONS : "buyer creates"
    FARMERS ||--o{ SUBSCRIPTIONS : "is followed"
    USERS ||--o{ NOTIFICATIONS : "receives"
```

## Notes

- `users.role` distinguishes buyers, farmers, and admins; a farmer also has one optional `farmers` profile linked through the unique `farmers.user_id`.
- `cart_items` and `subscriptions` are associative tables with uniqueness constraints to prevent duplicate product entries per buyer and duplicate follows per buyer/farmer pair.
- `order_items` stores both `product_id` and `farmer_id`, which snapshots who fulfills each item even though the product already belongs to a farmer.
- All foreign keys use `ON DELETE CASCADE`, so deleting a parent row removes dependent records.
