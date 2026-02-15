# SCRUM BOOK
## Online Platform for Buying and Selling Used and Unused Items Inside Campus

---

| **Project Title** | Online Platform for Buying and Selling Used and Unused Items Inside Campus |
|---|---|
| **Technology Stack** | Flask, MySQL, HTML/CSS, Bootstrap 5, Python, OpenCV, TensorFlow (MobileNetV2) |
| **Methodology** | Agile – Scrum Framework |
| **Sprint Duration** | 1 Week per Sprint |

---

## Daily Scrum Log

| Date | Work Done |
|---|---|
| **13/01/26** | **Overall review & next phase preparation.** Today, the overall work done in the past two weeks was reviewed. All planning, analysis and testing activities were consolidated. Steps & improvements were identified. The documents were modified. This ensures a smooth transition to development. |
| **14/01/26** | **Designed the homepage interface.** Designed a visually appealing homepage with a clean layout, hero image, project description and call-to-action button. Ensured the navigation bar clearly communicated the purpose of the campus marketplace platform. |
| **16/01/26** | **Updated navigation bar & developed profile page.** Updated the navigation bar across all pages to maintain consistency. Added buttons like Home, Dashboard, Sell Item, Browse Items, Profile and Logout with proper routing and UI design. Designed and developed the profile page displaying user details such as name, email, phone, department, semester and profile picture. Added option to update profile details and upload profile image. |
| **17/01/26** | **Linked user profile with posted items & item management.** Implemented functionality to display all items posted by the logged-in user on the profile page. Added edit and delete options for managing posted items. Developed backend logic and form for editing item details. Implemented delete functionality with confirmation prompts to prevent accidental deletion of items. |
| **18/01/26** | **Developed the Sell Item page.** Created the "Sell Item" page with input fields for product title, description, price, category and item condition. Added image upload functionality with live preview. Designed the form layout using Bootstrap 5 cards for a clean user interface. |
| **20/01/26** | **Implemented Sell Item backend logic.** Developed backend logic to store item details in the MySQL `products` table. Implemented secure image upload with UUID-based filenames to prevent conflicts. Images are saved to the `static/uploads/` server directory. Tested posting items successfully end-to-end. |
| **21/01/26** | **Developed the Browse Item page.** Created the "Browse Item" page displaying all available products in a responsive card grid layout. Each card shows product image, title, price, seller name and category badge. Ensured visibility of items across campus for better usability. |
| **22/01/26** | **Added search and filter functionality to Browse Item page.** Implemented keyword-based search filtering by title and description. Added category dropdown filter and price sorting options (Low to High, High to Low, Newest, Oldest). Tested all filters for correct results. |
| **23/01/26** | **Developed the messaging system.** Created the messaging module allowing buyers to contact sellers directly through the platform. Designed the messages listing page showing all conversations. Implemented backend routes for sending and receiving messages. |
| **24/01/26** | **Completed chat interface and message display.** Developed the real-time chat interface displaying message history between buyer and seller. Added timestamp display for each message. Implemented form for sending new messages within the chat window. Tested the complete messaging flow between two users. |
| **25/01/26** | **Planned the AI image analysis module.** Researched suitable AI/ML models for image quality analysis. Selected MobileNetV2 as a lightweight pre-trained model for condition classification. Identified OpenCV's Laplacian variance method for blur detection. Outlined the four AI sub-modules: blur detection, condition classification, feedback generation, and trust scoring. |
| **27/01/26** | **Implemented blur detection module.** Developed `blur_detector.py` using OpenCV's Laplacian variance method to detect blurry product images. Defined blur threshold and scoring logic. Tested blur detection with clear and blurry sample images. Results correctly identify image sharpness levels. |
| **28/01/26** | **Implemented condition classifier using MobileNetV2.** Developed `condition_classifier.py` using a pre-trained MobileNetV2 model combined with image feature analysis. The classifier categorizes products into Good, Moderate and Damaged conditions. Added confidence score calculation for each classification. |
| **29/01/26** | **Developed feedback generator and trust score calculator.** Created `feedback_generator.py` with template-based logic to generate human-readable improvement suggestions. Developed `trust_scorer.py` to calculate a composite trust score (0–100) based on image quality, condition and description quality using weighted formula. |
| **30/01/26** | **Integrated AI module into product upload flow.** Connected all four AI sub-modules into the main `ai_module/__init__.py` orchestrator. Integrated AI analysis into the `/add_product` route so every uploaded product is automatically analyzed. AI results (blur score, condition, trust score, feedback) are stored in the `product_ai_analysis` table. |
| **31/01/26** | **Implemented live AI preview on Sell Item page.** Created AJAX endpoint `/api/analyze_image` for real-time AI feedback during product upload. Added JavaScript to trigger live analysis when image is selected. Users can now see AI trust score, condition label and improvement tips before submitting the form. |
| **01/02/26** | **Displayed AI analysis on product detail page.** Updated the product detail page to show the AI Analysis Report section including trust score badge, blur detection result, condition classification with confidence percentage, and AI-generated feedback tips. Styled the report with color-coded badges and progress bars. |
| **03/02/26** | **Planned and started admin module development.** Designed the admin module architecture with role-based access control. Added 'admin' role to the users table ENUM. Created default admin account. Developed the admin routes blueprint with `admin_required` decorator for access protection. |
| **04/02/26** | **Developed admin dashboard with platform statistics.** Created the admin dashboard page displaying total users, active listings, items sold, average trust score, total messages, categories and AI-analyzed products. Added recent users and recent products tables. Implemented category distribution chart and AI condition distribution summary. |
| **05/02/26** | **Developed user and product management pages.** Created the user management page with search/filter by name, email and role. Added role promotion/demotion and delete user functionality. Developed the product management page with search, status filter and category filter. Added toggle status (available/removed) and permanent delete options for products. |
| **06/02/26** | **Developed category management and AI analytics pages.** Created the category management page with add, edit (modal) and delete functionality. Developed the AI Analytics page showing blur statistics, condition distribution, average trust score summary and detailed analysis table for all products. |
| **07/02/26** | **Integrated admin module and updated navigation.** Registered the admin blueprint in `app.py`. Updated the login route to store user role in session and redirect admin users to admin dashboard. Added Admin link in the navigation bar visible only to admin users. Tested all admin routes for correct access control — non-admin users are blocked. |
| **10/02/26** | **Conducted integration testing and bug fixes.** Ran comprehensive end-to-end tests covering user registration, login, product posting with AI analysis, browsing, messaging and admin operations. Fixed schema mismatch issues in the database. Verified all pages return HTTP 200 status. Resolved image path and template rendering issues. |
| **12/02/26** | **UI polishing, responsive testing and trust badge improvements.** Refined the frontend UI across all pages. Ensured mobile responsiveness on all templates. Improved trust score badge colors and added gradient stat cards on admin dashboard. Verified cross-browser compatibility and consistent styling. |
| **14/02/26** | **Final testing, code cleanup and documentation.** Performed final round of testing on all features — dashboard, sell item, browse item, profile, messaging, AI analysis and admin module. Cleaned up unused code and temporary files. Prepared the Scrum documentation and sprint reports. |
| **15/02/26** | **Project review and submission preparation.** Consolidated all project deliverables including source code, database schema, Scrum book and test reports. Reviewed the complete application functionality with all modules working end-to-end. Platform is ready for demonstration and submission. |

---

## SPRINT 1: Dashboard Page Development

| **Field** | **Details** |
|---|---|
| **Sprint Goal** | Design and implement the main dashboard page with navigation and feature overview |
| **Sprint Duration** | Week 1 |
| **Status** | ✅ Completed |

### Sprint Backlog

| # | User Story / Task | Priority | Status |
|---|---|---|---|
| 1.1 | As a user, I want a dashboard page so that I can access all features from one place | High | ✅ Done |
| 1.2 | Display navigation options: Sell Item, Browse Item, Profile, Logout | High | ✅ Done |
| 1.3 | Add descriptive feature cards explaining available features | Medium | ✅ Done |
| 1.4 | Implement responsive layout using Bootstrap 5 | Medium | ✅ Done |
| 1.5 | Add campus-themed branding and styling | Low | ✅ Done |

### Work Done

- **Dashboard Page:** Designed and developed the main dashboard page as the central hub after user login. The page provides a clean, organized layout for navigating the platform.

- **Navigation Options:** Implemented navigation links for:
  - **Sell Item** – Directs users to the product listing form
  - **Browse Items** – Opens the marketplace to view all available products
  - **Profile** – Shows user profile information
  - **Logout** – Securely ends the user session

- **Feature Cards:** Added descriptive cards on the dashboard that explain the available features to improve user experience. Each card contains an icon, title, and a brief description of the feature, helping first-time users understand the platform capabilities quickly.

- **UI/UX Enhancements:** Used Bootstrap 5 card components with gradient backgrounds, hover animations, and icons to make the dashboard visually appealing and intuitive.

### Sprint Review

| Criteria | Result |
|---|---|
| Dashboard loads successfully | ✅ Pass |
| All navigation links functional | ✅ Pass |
| Feature cards displayed correctly | ✅ Pass |
| Responsive on mobile/tablet | ✅ Pass |

---

## SPRINT 2: Sell Item Page Development

| **Field** | **Details** |
|---|---|
| **Sprint Goal** | Develop the "Sell Item" page for listing products with image upload |
| **Sprint Duration** | Week 2 |
| **Status** | ✅ Completed |

### Sprint Backlog

| # | User Story / Task | Priority | Status |
|---|---|---|---|
| 2.1 | As a seller, I want a form to enter item details so I can list my product | High | ✅ Done |
| 2.2 | Implement input fields: Title, Description, Price, Category, Condition | High | ✅ Done |
| 2.3 | Add image upload functionality with preview | High | ✅ Done |
| 2.4 | Store item details in MySQL database | High | ✅ Done |
| 2.5 | Save uploaded images to server directory | High | ✅ Done |
| 2.6 | Add form validation (required fields, price > 0) | Medium | ✅ Done |
| 2.7 | Test posting items end-to-end | High | ✅ Done |

### Work Done

- **Sell Item Form:** Developed the "Sell Item" page (`/add_product`) with a comprehensive form containing the following input fields:
  - **Product Title** – Text field for item name
  - **Description** – Text area for detailed item description
  - **Price (₹)** – Numeric input for item price
  - **Category** – Dropdown selection (Books, Electronics, Clothing, Furniture, Sports, Stationery, Accessories, Other)
  - **Item Condition** – Selection (New, Like New, Used, Heavily Used)
  - **Product Image** – File upload with live image preview

- **Image Upload Logic:** Implemented secure image upload functionality:
  - Images are validated for allowed formats (JPG, PNG, GIF, WebP)
  - Each image is saved with a unique UUID-based filename to prevent conflicts
  - Images are stored in the `static/uploads/` server directory
  - Live preview is shown to the seller before submission

- **Database Storage:** Item details (title, description, price, category, condition, image filename, seller ID) are stored in the `products` table in MySQL database upon form submission.

- **AI Integration:** Upon successful upload, the product image is automatically analyzed by the AI module for blur detection, condition classification, and trust score calculation. Results are stored in the `product_ai_analysis` table.

- **Testing:** Successfully tested the complete flow of posting items – from form entry, image upload, database insertion, to viewing the listed item with AI analysis results.

### Sprint Review

| Criteria | Result |
|---|---|
| Form renders with all fields | ✅ Pass |
| Image upload and preview works | ✅ Pass |
| Data stored in MySQL correctly | ✅ Pass |
| Image saved to server directory | ✅ Pass |
| AI analysis runs after upload | ✅ Pass |
| Form validation works | ✅ Pass |

---

## SPRINT 3: Browse Item Page Development

| **Field** | **Details** |
|---|---|
| **Sprint Goal** | Develop the "Browse Item" page with search and filtering capabilities |
| **Sprint Duration** | Week 3 |
| **Status** | ✅ Completed |

### Sprint Backlog

| # | User Story / Task | Priority | Status |
|---|---|---|---|
| 3.1 | As a buyer, I want to browse all available items listed on the platform | High | ✅ Done |
| 3.2 | Display items in a responsive grid layout with image, title, price | High | ✅ Done |
| 3.3 | Add search functionality to find items by name/description | High | ✅ Done |
| 3.4 | Add category filter to filter items by category | High | ✅ Done |
| 3.5 | Add price-based sorting (Low to High, High to Low) | Medium | ✅ Done |
| 3.6 | Show AI trust score badge on each product card | Medium | ✅ Done |
| 3.7 | Ensure visibility of items across campus for better usability | Medium | ✅ Done |

### Work Done

- **Browse Item Page:** Developed the "Browse Item" page (`/`) displaying all available products posted by campus users in a responsive card grid layout. Each product card shows:
  - Product image thumbnail
  - Product title
  - Price (in ₹)
  - Seller name
  - Category badge
  - AI Trust Score indicator

- **Search Functionality:** Implemented keyword-based search that filters products by matching the search term against product title and description fields. Users can quickly find specific items using the search bar.

- **Category Filter:** Added a category dropdown filter allowing users to filter products by category (Books, Electronics, Clothing, Furniture, Sports, Stationery, Accessories, Other). Selecting a category shows only products in that category.

- **Price Filter / Sorting:** Implemented sorting options for users to organize results:
  - **Newest First** – Most recently listed items appear first (default)
  - **Oldest First** – Earliest listed items appear first
  - **Price: Low to High** – Sorted by ascending price
  - **Price: High to Low** – Sorted by descending price
  - **Trust Score** – Sorted by AI trust score (highest first)

- **Campus-Wide Visibility:** All items listed by any campus user are visible to all other authenticated users, ensuring maximum visibility and reach within the campus community. This replaces informal methods like WhatsApp groups and notice boards with a structured, searchable platform.

### Sprint Review

| Criteria | Result |
|---|---|
| All available products displayed | ✅ Pass |
| Search by keyword works | ✅ Pass |
| Category filter works | ✅ Pass |
| Price/sort filter works | ✅ Pass |
| Trust score badges shown | ✅ Pass |
| Responsive grid layout | ✅ Pass |
| Cross-campus item visibility | ✅ Pass |

---

## Sprint Velocity Summary

| Sprint | Planned Tasks | Completed | Velocity |
|---|---|---|---|
| Sprint 1 – Dashboard | 5 | 5 | 100% |
| Sprint 2 – Sell Item | 7 | 7 | 100% |
| Sprint 3 – Browse Item | 7 | 7 | 100% |
| **Total** | **19** | **19** | **100%** |

---

## Product Backlog (Remaining)

| # | Feature | Priority | Status |
|---|---|---|---|
| 4.1 | User Profile Management | Medium | ✅ Completed |
| 4.2 | In-Platform Messaging System | Medium | ✅ Completed |
| 4.3 | AI-Based Image Analysis & Trust Scoring | High | ✅ Completed |
| 4.4 | Admin Module (Dashboard, User/Product/Category Management) | High | ✅ Completed |

---

## Tools & Technologies Used

| Category | Tool/Technology |
|---|---|
| Backend | Flask (Python) |
| Database | MySQL |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| AI/ML | OpenCV (Blur Detection), TensorFlow/Keras (MobileNetV2) |
| Image Processing | Pillow, NumPy |
| IDE | VS Code |
| Version Control | Git |
| Methodology | Agile – Scrum |

---

*Document prepared as part of MCA Final Year Project — 2026*
