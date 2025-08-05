# Frontend Documentation

This document provides an overview of the frontend application, including its architecture, state management, and core components.

## 1. Architecture and Technology Stack

The frontend is a modern Single Page Application (SPA) built with **Next.js** and **React**, using **TypeScript** for type safety.

- **Framework:** Next.js (using the App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS, with `clsx` and `tailwind-merge` for utility class management.
- **UI Components:** A combination of custom-built components and primitives from **Radix UI**, indicating a design system-oriented approach. This makes the UI consistent and accessible.
- **State Management:** A hybrid approach using:
  - **Zustand:** For global client-side state that is shared across many components (e.g., dashboard view, analysis reports).
  - **React Context API:** For self-contained, feature-specific state, most notably for authentication (`AuthProvider`).
- **Data Fetching:** **Axios** is used for all HTTP requests to the backend API.
- **Charts:** **Chart.js** is used for data visualization.

## 2. Project Structure

- **`/app`**: The core of the application, following the Next.js App Router convention.
  - **`layout.tsx`**: The root layout of the application. It sets up the global font, AuthProvider, and other top-level components.
  - **`/auth`**: Contains the login and registration pages.
  - **`/dashboard`**: The main dashboard view after a user logs in.
  - **`/demo-enhanced-builder`**: A page for a more advanced rule builder interface.

- **`/components`**: Contains all the reusable React components, organized by feature.
  - **`/ui`**: Generic, reusable UI elements like `Button`, `Card`, `Input`, etc. These are the building blocks of the application's design system.
  - **`/dashboard`**: Components specific to the main dashboard, such as `Sidebar`, `Header`, and various charts.
  - **`/rules`**: Components for creating, editing, and managing warehouse rules.
  - **`/analysis`**: Components for the file upload and column mapping process.

- **`/lib`**: Contains shared logic, utilities, and type definitions.
  - **`api.ts`**: The configured Axios instance. This is the central point for all backend API communication. It includes interceptors to automatically add the JWT authentication token to requests and handle 401 (Unauthorized) errors.
  - **`auth.ts` / `auth-context.tsx`**: Manages user authentication state and provides it to the rest of the application via a React Context.
  - **`store.ts` / `rules-store.ts`**: Defines the Zustand stores for managing global state related to the dashboard and rules.
  - **`hooks/`**: Contains custom React hooks for reusable logic.

## 3. State Management

The application uses a combination of Zustand and React Context for state management.

- **`useAuthStore` (in `lib/store.ts`):** A Zustand store that holds the authenticated user's information and authentication status. It includes actions for logging in, logging out, and initializing the auth state from `localStorage`.
- **`useDashboardStore` (in `lib/store.ts`):** A Zustand store that manages the state of the main dashboard, including the current view, a list of analysis reports, and the currently selected report.
- **`AuthProvider` (in `lib/auth-context.tsx`):** A React Context provider that wraps the entire application in `app/layout.tsx`. It makes the authentication state available to all components.

## 4. API Interaction

All communication with the backend is handled through the pre-configured Axios instance in `lib/api.ts`.

- **Request Interceptor:** Before any request is sent, an interceptor checks if an `auth_token` exists in `localStorage`. If it does, the interceptor automatically adds the `Authorization: Bearer <token>` header to the request.
- **Response Interceptor:** If the backend responds with a `401 Unauthorized` status, the response interceptor will automatically clear the user's authentication data from `localStorage` and redirect them to the login page. This provides a seamless and secure authentication experience.
