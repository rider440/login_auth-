# 🏗️ Frontend Folder Structure Guide

This guide explains the project structure of our Next.js application, why we use specific folders, and when to add new files to them.

---

## 📁 Root Directory Structure

```text
frontend/
├── app/                # Next.js App Router (Routes, Layouts, Pages)
├── components/         # Reusable UI Components
├── services/           # API Integration & Business Logic
├── public/             # Static Assets (Images, Icons, Fonts)
├── next.config.mjs     # Next.js Configuration
├── package.json        # Dependencies & Scripts
└── tsconfig.json       # TypeScript Configuration
```

---

## 📂 1. `app/` (The Heart of Routing)

**Why use it?** Next.js 13+ uses the "App Router". Every folder inside `app/` that contains a `page.tsx` file becomes a public route.

*   **`layout.tsx`**: Defines the shared UI for a segment and its children (e.g., Navbar, Footer).
*   **`page.tsx`**: The unique UI for a specific route.
*   **`globals.css`**: Global styles applied across the entire app.

**When to use?**
- Use `app/login/page.tsx` when you want to create a `/login` URL.
- Use `app/layout.tsx` to wrap your app in providers or shared layouts.

---

## 📂 2. `components/` (Reusable UI)

**Why use it?** To keep code DRY (Don't Repeat Yourself). Components here should be "dumb" or "semi-smart" UI pieces that can be reused across different pages.

*   **Example**: `AuthCard.tsx`
    ```tsx
    // Why: To provide a consistent "glassmorphism" look for all auth forms.
    export const AuthCard = ({ children }) => (
      <div className="glass-card">{children}</div>
    );
    ```

**When to use?**
- If you find yourself writing the same HTML/CSS in two different pages.
- To break down a large page (like `RegisterForm.tsx`) into smaller, manageable pieces.

---

## 📂 3. `services/` (The Communication Layer)

**Why use it?** To centralize all API calls. Instead of using `fetch` or `axios` directly inside components, we keep them here. This makes it easier to update the Backend URL or handle global error logic.

*   **Example**: `api.ts`
    ```ts
    // Why: Centralized logic for talking to the FastAPI backend.
    export const sendOTP = async (phone: string) => {
      const response = await fetch(`${API_URL}/send-otp`, { ... });
      return response.json();
    };
    ```

**When to use?**
- Whenever you need to fetch data from or send data to the backend.
- When you need to transform API data before it reaches your UI.

---

## 📂 4. `public/` (Static Assets)

**Why use it?** For files that don't change and need to be served as-is.

**When to use?**
- Storing the company logo (`logo.png`).
- Custom fonts or static SVG icons.

---

## 📝 Best Practices & Naming Conventions

1.  **Components**: Use **PascalCase** (e.g., `LoginForm.tsx`).
2.  **Styles**: Use **CSS Variables** in `globals.css` for colors and spacing to maintain consistency.
3.  **Services**: Use descriptive function names (e.g., `verifyUserOTP` instead of just `verify`).
4.  **Routes**: Use lowercase folder names in `app/` (e.g., `app/register/`).

---

## 💡 Example: Adding a "Profile" Feature

1.  **Service**: Add `getUserProfile` to `services/api.ts`.
2.  **Component**: Create `ProfileHeader.tsx` in `components/`.
3.  **Page**: Create `app/profile/page.tsx` and use the service and component there.
