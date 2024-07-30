# Daily Expenses Sharing Application

## Project Overview

This project is a backend service for a daily expenses sharing application. It allows users to manage and split expenses among participants using three different methods: equal, exact amounts, and percentage-based splits. The application handles user management, expense tracking, and generates downloadable balance sheets.

## Features

- **User Management:**
  - Users can sign up with their email, name, and mobile number.
  - Users can authenticate using JWT tokens.
- **Expense Management:**

  - Users can add expenses and split them using the following methods:
    1. **Equal:** The total amount is split equally among all participants.
    2. **Exact:** Each participant is assigned an exact amount they owe.
    3. **Percentage:** The amount owed by each participant is based on a percentage of the total expense.

- **Balance Sheet:**
  - The system provides an individual balance sheet showing all expenses a user has paid.
  - Users can download the balance sheet as a PDF or CSV file.

## Installation and Setup

### Prerequisites

```
- Python 3.x
- Django 4.x
- Django REST Framework
- Django SimpleJWT
- xhtml2pdf
```

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/regmi-keshav/expenses-sharing-app.git
   cd daily-expenses-sharing-app
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations:**

   ```bash
   python manage.py migrate
   ```

4. **Create a superuser:**
   If you want to have a superuser to manage all the users.

   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server:**

   ```bash
   python manage.py runserver
   ```

## API Endpoints

### User Endpoints

1. **Register a new user**

   - **URL:** `/api/users/`
   - **Method:** `POST`
   - **Description:** Create a new user.
   - **Request Body:**
     ```json
     {
       "email": "user@example.com",
       "name": "John Doe",
       "mobile_number": "1234567890",
       "password": "password123"
     }
     ```
   - **Response:**
     ```json
     {
       "id": 1,
       "email": "user@example.com",
       "name": "John Doe",
       "mobile_number": "1234567890"
     }
     ```

2. **User Login (Obtain JWT Token)**

   - **URL:** `/api/token/`
   - **Method:** `POST`
   - **Description:** Obtain JWT tokens for user authentication.
   - **Request Body:**
     ```json
     {
       "email": "user@example.com",
       "password": "password123"
     }
     ```
   - **Response:**
     ```json
     {
       "access": "access_token",
       "refresh": "refresh_token"
     }
     ```

3. **Retrieve User Details**

   - **URL:** `/api/users/`
   - **Method:** `GET`
   - **Description:** List all users.
   - **Headers:**
     - `Authorization: Bearer <access_token>`
   - **Response:**

     ```json
     [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe",
            "mobile_number": "1234567890"
        },

         .
         .
         .
     ]
     ```

4. **Retrieve User**

   - **Endpoint:** `/api/users/{id}/`
   - **Method:** `GET`
   - **Description:** Retrieve details of a specific user.
   - **Headers:** `Authorization: Bearer <your-access-token>`
   - **Response:**
     ```json
     {
       "id": 1,
       "email": "user@example.com",
       "name": "John Doe",
       "mobile_number": "1234567890"
     }
     ```

5. **Update User**

   - **Endpoint:** `/api/users/{id}/`
   - **Method:** `PUT`
   - **Description:** Update a specific user.
   - **Request Body:**

     ```json
     {
       "username": "updated_user",
       "email": "updated_user@example.com"
     }
     ```

   - **Response:**
     ```json
     {
       "id": 1,
       "username": "updated_user",
       "email": "updated_user@example.com"
     }
     ```

6. **Delete User Account**
   - **URL:** `/api/users/{id}/`
   - **Method:** `DELETE`
   - **Description:** Delete a specific user.
   - **Headers:**
     - `Authorization: Bearer <access_token>`
   - **Response:**
     ```json
     {
       "detail": "User has been deleted."
     }
     ```

### Expense Endpoints

1.  **Add a New Expense**

    - **URL:** `/api/expenses/`
    - **Method:** `POST`
    - **Description:** Create a new expense.
    - **Headers:**
      - `Authorization: Bearer <access_token>`
    - **Example 1: Equal Split Method**
      **Scenario:** You go out with 3 friends. The total bill is 3000. Now, each friend owes 1000.

    - **Request Body:**
      ```json
      {
        "payer": 1, // ID of the user who paid
        "total_amount": "3000.00",
        "split_method": "equal",
        "description": "Dinner at restaurant",
        "date": "2024-08-25", // ID of the users to split with
        "splits": [{ "user": 1 }, { "user": 2 }, { "user": 3 }]
      }
      ```
    - **Response:**

      ```json
      {
        "id": 1,
        "payer": 1,
        "total_amount": "3000.00",
        "split_method": "equal",
        "description": "Dinner at restaurant",
        "date": "2024-08-25",
        "splits": [
          {
            "user": 1,
            "amount": "1000.00",
            "percentage": "33.33"
          },
          {
            "user": 2,
            "amount": "1000.00",
            "percentage": "33.33"
          },
          {
            "user": 3,
            "amount": "1000.00",
            "percentage": "33.33"
          }
        ]
      }
      ```

    - **Example 2: Exact Split Method**

      **Scenario:** You go to shopping with two friends and pay 4299. Friend 1 owes 799, Friend 2 owes 2000, and you owe 1500.

    - **Request Body**

      ```json
      {
        "payer": 1,
        "total_amount": "4299.00",
        "split_method": "exact",
        "description": "Shopping",
        "date": "2024-08-25",
        "splits": [
          { "user": 1, "amount": "1500.00" },
          { "user": 2, "amount": "799.00" },
          { "user": 3, "amount": "2000.00" }
        ]
      }
      ```

    - **Response**

      ```json
      {
        "id": 1,
        "payer": 1,
        "total_amount": "4299.00",
        "split_method": "exact",
        "description": "Shopping",
        "date": "2024-08-25",
        "splits": [
          {
            "user": 1,
            "amount": "1500.00",
            "percentage": "34.91"
          },
          {
            "user": 2,
            "amount": "799.00",
            "percentage": "18.59"
          },
          {
            "user": 3,
            "amount": "2000.00",
            "percentage": "46.50"
          }
        ]
      }
      ```

    - **Example 3: Percentage Split Method**

      **Scenario:** You go to a party with 2 friends and one of your cousins. You owe 50%, Friend 1 owes 25%, and Friend 2 owes 25%.

    - **Request Body**

      ```json
      {
        "payer": 1,
        "total_amount": "3000.00",
        "split_method": "percentage",
        "description": "Party",
        "date": "2024-08-25",
        "splits": [
          {
            "user": 1,
            "percentage": "50.00"
          },
          {
            "user": 2,
            "percentage": "25.00"
          },
          {
            "user": 3,
            "percentage": "25.00"
          }
        ]
      }
      ```

    - **Response**

      ```json
      {
        "id": 2,
        "payer": 1,
        "total_amount": "3000.00",
        "split_method": "percentage",
        "description": "Party",
        "date": "2024-08-25",
        "splits": [
          {
            "user": 1,
            "percentage": "50.00",
            "amount": "1500.00"
          },
          {
            "user": 2,
            "percentage": "25.00",
            "amount": "750.00"
          },
          {
            "user": 3,
            "percentage": "25.00",
            "amount": "750.00"
          }
        ]
      }
      ```

2.  **Retrieve User's Individual Expenses**

- **URL:** `/api/expenses/user_expenses/`
- **Method:** `GET`
- **Description:** This endpoint retrieves all expenses that were created by the authenticated user. It filters the expenses based on the currently logged-in user.
- **Headers:**
  - `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  [
    {
      "id": 1,
      "payer": 1,
      "total_amount": "3000.00",
      "split_method": "equal",
      "description": "Dinner at restaurant",
      "date": "2024-08-25",
      "splits": [
        {
           "user": 1,
           "amount": "1000.00",
           "percentage": "33.33"
        },
        {
           "user": 2,
           "amount": "1000.00",
           "percentage": "33.33"
        },
        {
          "user": 3,
          "amount": "1000.00",
           "percentage": "33.33"
        }
      ]
    },
    .
    .
    .
  ]
  ```

3.  **Retrieve Expense**

    - **Endpoint:** `/api/expenses/{id}/`
    - **Method:** `GET`
    - **Description:** Retrieve details of a specific expense.
    - **Headers:** `Authorization: Bearer     <your-access-token>`
    - **Response:**

      ```json
      {
        "id": 1,
        "payer": 1,
        "total_amount": "3000.00",
        "split_method": "equal",
        "description": "Dinner at restaurant",
        "date": "2024-08-25",
        "splits": [
          {
            "user": 1,
            "amount": "1000.00",
            "percentage": "33.33"
          },
          {
            "user": 2,
            "amount": "1000.00",
            "percentage": "33.33"
          },
          {
            "user": 3,
            "amount": "1000.00",
            "percentage": "33.33"
          }
        ]
      }
      ```

4.  **Retrieve Overall Expenses**

    - **URL:** `/api/expenses/overall_expenses/`
    - **Method:** `GET`
    - **Description:** This endpoint retrieves a list of all expenses in the system, regardless of the user. It shows all expenses that have been created, not just those by the authenticated user.
    - **Headers:**
      - `Authorization: Bearer <access_token>`
    - **Response:**

      ```json
      [
        {
          "id": 1,
          "payer": 1,
          "total_amount": "3000.00",
          "split_method": "equal",
          "description": "Dinner at restaurant",
          "date": "2024-08-25",
          "splits": [
            {
              "user": 1,
              "amount": "1000.00",
              "percentage": "33.33"
            },

            {
              "user": 2,
              "amount": "1000.00",
              "percentage": "33.33"
            },

            {
              "user": 3,
              "amount": "1000.00",
              "percentage": "33.33"
            }
          ]
        }
      ]
      ```

5.  **Update Expense**

    - **Endpoint:** `/api/expenses/{id}/`
    - **Method:** `PUT`
    - **Description:** Update a specific expense.
    - **Request Body:**
      ```json
      {
        "payer": 1,
        "total_amount": "600.00",
        "split_method": "percentage",
        "description": "Lunch",
        "date": "2024-08-26",
        "splits": [
          {
            "user": 1,
            "percentage": "50.00"
          },
          {
            "user": 2,
            "percentage": "50.00"
          }
        ]
      }
      ```
    - **Response:**
      ```json
      {
        "id": 1,
        "payer": 1,
        "total_amount": "600.00",
        "split_method": "percentage",
        "description": "Lunch",
        "date": "2024-08-26",
        "splits": [
          {
            "user": 1,
            "amount": "300.00",
            "percentage": "50.00"
          },
          {
            "user": 2,
            "amount": "300.00",
            "percentage": "50.00"
          }
        ]
      }
      ```

6.  **Delete Expense**

    - **Endpoint:** `/api/expenses/{id}/`
    - **Method:** `DELETE`
    - **Description:** Delete a specific expense.
    - **Headers:** `Authorization: Bearer     <your-access-token>`
    - **Response:**
      ```json
      {
        "detail": "Expense has been deleted."
      }
      ```

7.  **Balance Sheet**

    - **Endpoint:** `/api/expenses/balance_sheet/`
    - **Method:** `GET`
    - **Description:** Retrieve a balance sheet showing all expenses created by the authenticated user.
    - **Headers:** `Authorization: Bearer     <your-access-token>`
    - **Response:**
      ```json
      {
        "user_expenses": [
          {
            "id": 1,
            "payer": 1,
            "total_amount": "500.00",
            "split_method": "exact",
            "description": "Dinner",
            "date": "2024-08-25",
            "splits": [
              {
                "user": 1,
                "amount": "200.00",
                "percentage": null
              },
              {
                "user": 2,
                "amount": "300.00",
                "percentage": null
              }
            ]
          }
        ],
        "total_expenses": "500.00"
      }
      ```

8.  **Download Balance Sheet (PDF)**

    - **URL:** `/api/expenses/download-balance-sheet/`
    - **Method:** `GET`
    - **Description:** Download a PDF of the balance sheet showing all expenses created by the authenticated user.
    - **Description:** Download a PDF of the balance sheet showing all expenses created by the authenticated user.
    - **Headers:**
      - `Authorization: Bearer <access_token>`
    - **Response:** PDF file containing balance sheet

9.  **Download User Expenses (CSV)**
    - **URL:** `/api/expenses/download-csv/`
    - **Method:** `GET`
    - **Description:** Download a csv file of the balance sheet showing all expenses created by the authenticated user.
    - **Headers:**
      - `Authorization: Bearer <access_token>`
    - **Response:** CSV file containing user expenses

## Authentication

This project uses JWT (JSON Web Token) for user authentication. The token can be obtained by sending a POST request to `/api/token/` with the user's email and password.

Include the token in the `Authorization` header of your requests as follows:

```
Authorization: Bearer <access_token>
```

## Error Handling

The application includes robust error handling mechanisms. Errors are returned with appropriate HTTP status codes and descriptive error messages.

## Testing

You can test the API endpoints using tools like Postman or Curl. Ensure to include the JWT token in the `Authorization` header for authenticated routes.

---

## License

**This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.**

Feel free to modify the endpoints and details according to your project's specifics.
