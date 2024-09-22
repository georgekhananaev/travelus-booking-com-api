# Hotel Booking API with FastAPI, Redis, and MongoDB

This project is a FastAPI-based API that interacts with the Booking.com API to fetch and cache hotel booking data. The API supports fetching hotel details, rooms, photos, and reviews, with Redis for caching and MongoDB as a persistent data store. It also provides options for concurrent hotel data fetching and handles multi-language responses.

## Features
- Fetch hotel data, including detailed hotel information, rooms, photos, and reviews.
- Support for fetching data from multiple hotels concurrently.
- Data caching using Redis for improved performance.
- Logging with rotating file handler for error and activity logs.
- Dockerized environment for easy setup and deployment.
- Secured with FastAPI basic authentication and Bearer tokens.

## Endpoints

### 1. **Get Hotel Data**
- **GET** `/hotel`
- Fetch data for a specific hotel.
- **Query Parameters**:
    - `hotel_id` (default: `4469654`)
    - `locale` (default: `en-gb`)

### 2. **Get Multiple Hotels Data**
- **GET** `/hotels/`
- Fetch data for multiple hotels concurrently.
- **Query Parameters**:
    - `hotel_ids`: List of hotel IDs (default: `[2534439, 4469654]`)
    - `locale` (default: `en-gb`)

### 3. **Get Hotel Photos**
- **GET** `/photos`
- Fetch photos for a specific hotel.
- **Query Parameters**:
    - `hotel_id` (default: `4469654`)
    - `locale` (default: `en-gb`)

### 4. **Get Hotel Reviews**
- **GET** `/reviews`
- Fetch reviews for a specific hotel.
- **Query Parameters**:
    - `hotel_id` (default: `4469654`)
    - `customer_type`, `sort_type`, `language_filter`, `page_number`

### 5. **Get Hotel Room List**
- **GET** `/room-list`
- Fetch the list of rooms for a specific hotel.
- **Query Parameters**:
    - `hotel_id` (default: `4469654`)
    - `checkin_date` (default: 30 days from today)
    - `checkout_date` (default: 31 days from today)
    - Other parameters: `children_ages`, `children_number_by_rooms`, `adults_number_by_rooms`, `units`, `currency`, `locale`

### 6. **Get Detailed Hotel Data**
- **GET** `/detailed_hotel`
- Fetch detailed hotel data, including rooms and photos, for one or more hotels.
- **Query Parameters**:
    - `hotel_ids`: List of hotel IDs (default: `[4469654]`)
    - `show_photos` (default: `True`)
    - `show_rooms` (default: `True`)

![API Usage](https://github.com/georgekhananaev/travelus-booking-com-api/blob/master/screenshots/api_usage.png?raw=true)

## Environment Variables

Set the following environment variables in a `.env` file:

```dotenv
# Timezone configuration
TIMEZONE_OFFSET_HOURS=7

# MongoDB Configuration
MDB_USERNAME=YOUR_MONGO_USERNAME
MDB_PASSWORD=YOUR_MONGO_PASSWORD
MDB_SERVER=YOUR_MONGO_SERVER

# Document expiration time in MongoDB
EXPIRE_HOURS=72

# RapidAPI Configuration for Booking.com API, the host can't be changed.
RAPIDAPI_HOST=booking-com-stable-api.p.rapidapi.com
RAPIDAPI_KEY=YOUR_RAPIDAPI_KEY

# FastAPI Authentication
FASTAPI_UI_USERNAME=YOUR_DOCS_USERNAME
FASTAPI_UI_PASSWORD=YOUR_DOCS_PASSWORD
BEARER_SECRET_KEY=YOUR_SECRET_KEY
```

## Setup and Running the Project

**Prerequisites**
* Python 3.8+
* Docker
* Redis
* MongoDB Atlas (or any MongoDB instance)

**Steps**

1. Clone the repository:
    ```bash
    git clone https://github.com/georgekhananaev/travelus-booking-com-api.git
    cd travelus-booking-com-api
    ```
2. Install the required packages:
    ```bash 
   docker-compose up --build
    ```
3. Access the FastAPI Swagger UI at `http://localhost:8088/docs` and test the endpoints.

# Copyrights
Developed by George Khananaev for The Travel Office US, 2024
This project was designed and developed to meet the needs of The Travel Office US, leveraging modern technologies such as FastAPI, Redis, and MongoDB to deliver a highly efficient and scalable hotel booking API. The solution was architected by George Khananaev in 2024, ensuring a robust and performance-driven API platform for seamless travel management and integration.