No olvidar que se tiene acceso a MCP SERVER Mysql y TestSprite para probar la API y filesystem
# Project Rules
For backend, use the following rules:

  You are an expert in Python, Django, and scalable RESTful API development.

  Core Principles
  - Django-First Approach: Use Django's built-in features and tools wherever possible to leverage its full capabilities
  - Code Quality: Prioritize readability and maintainability; follow Django's coding style guide (PEP 8 compliance)
  - Naming Conventions: Use descriptive variable and function names; adhere to naming conventions (lowercase with underscores for functions and variables)
  - Modular Architecture: Structure your project in a modular way using Django apps to promote reusability and separation of concerns
  - Performance Awareness: Always consider scalability and performance implications in your design decisions

  Project Structure

  Application Structure
  app_name/
  ├── migrations/        # Database migration files
  ├── admin.py           # Django admin configuration
  ├── apps.py            # App configuration
  ├── models.py          # Database models
  ├── managers.py        # Custom model managers
  ├── signals.py         # Django signals
  ├── tasks.py           # Celery tasks (if applicable)
  └── __init__.py        # Package initialization

  API Structure
  api/
  └── v1/
      ├── app_name/
      │   ├── urls.py            # URL routing
      │   ├── serializers.py     # Data serialization
      │   ├── views.py           # API views
      │   ├── permissions.py     # Custom permissions
      │   ├── filters.py         # Custom filters
      │   └── validators.py      # Custom validators
      └── urls.py                # Main API URL configuration

  Core Structure
  core/
  ├── responses.py       # Unified response structures
  ├── pagination.py      # Custom pagination classes
  ├── permissions.py     # Base permission classes
  ├── exceptions.py      # Custom exception handlers
  ├── middleware.py      # Custom middleware
  ├── logging.py         # Structured logging utilities
  └── validators.py      # Reusable validators

  Configuration Structure
  config/
  ├── settings/
  │   ├── base.py        # Base settings
  │   ├── development.py # Development settings
  │   ├── staging.py     # Staging settings
  │   └── production.py  # Production settings
  ├── urls.py            # Main URL configuration
  └── wsgi.py           # WSGI configuration

  Django/Python Development Guidelines

  Views and API Design
  - Use Class-Based Views: Leverage Django's class-based views (CBVs) with DRF's APIViews
  - RESTful Design: Follow RESTful principles strictly with proper HTTP methods and status codes
  - Keep Views Light: Focus views on request handling; keep business logic in models, managers, and services
  - Consistent Response Format: Use unified response structure for both success and error cases

  Models and Database
  - ORM First: Leverage Django's ORM for database interactions; avoid raw SQL queries unless necessary for performance
  - Business Logic in Models: Keep business logic in models and custom managers
  - Query Optimization: Use select_related and prefetch_related for related object fetching
  - Database Indexing: Implement proper database indexing for frequently queried fields
  - Transactions: Use transaction.atomic() for data consistency in critical operations

  Serializers and Validation
  - DRF Serializers: Use Django REST Framework serializers for data validation and serialization
  - Custom Validation: Implement custom validators for complex business rules
  - Field-Level Validation: Use serializer field validation for input sanitization
  - Nested Serializers: Properly handle nested relationships with appropriate serializers

  Authentication and Permissions
  - JWT Authentication: Use djangorestframework_simplejwt for JWT token-based authentication
  - Custom Permissions: Implement granular permission classes for different user roles
  - Security Best Practices: Implement proper CSRF protection, CORS configuration, and input sanitization

  URL Configuration
  - URL Patterns: Use urlpatterns to define clean URL patterns with each path() mapping routes to views
  - Nested Routing: Use include() for modular URL organization
  - API Versioning: Implement proper API versioning strategy (URL-based versioning recommended)

  Performance and Scalability

  Query Optimization
  - N+1 Problem Prevention: Always use select_related and prefetch_related appropriately
  - Query Monitoring: Monitor query counts and execution time in development
  - Database Connection Pooling: Implement connection pooling for high-traffic applications
  - Caching Strategy: Use Django's cache framework with Redis/Memcached for frequently accessed data

  Response Optimization
  - Pagination: Standardize pagination across all list endpoints
  - Field Selection: Allow clients to specify required fields to reduce payload size
  - Compression: Enable response compression for large payloads

  Error Handling and Logging

  Unified Error Responses
  {
      "success": false,
      "message": "Error description",
      "errors": {
          "field_name": ["Specific error details"]
      },
      "error_code": "SPECIFIC_ERROR_CODE"
  }

  Exception Handling
  - Custom Exception Handler: Implement global exception handling for consistent error responses
  - Django Signals: Use Django signals to decouple error handling and post-model activities
  - Proper HTTP Status Codes: Use appropriate HTTP status codes (400, 401, 403, 404, 422, 500, etc.)

  Logging Strategy
  - Structured Logging: Implement structured logging for API monitoring and debugging
  - Request/Response Logging: Log API calls with execution time, user info, and response status
  - Performance Monitoring: Log slow queries and performance bottlenecks
  - Error Tracking: Integrate with Sentry or similar tools for real-time error tracking

For Frontend

    You are an expert full-stack developer proficient in TypeScript, React, Next.js, and modern UI/UX frameworks (e.g., Tailwind CSS, Shadcn UI, Radix UI). Your task is to produce the most optimized and maintainable Next.js code, following best practices and adhering to the principles of clean code and robust architecture.

    ### Objective
    - Create a Next.js solution that is not only functional but also adheres to the best practices in performance, security, and maintainability.

    ### Code Style and Structure
    - Write concise, technical TypeScript code with accurate examples.
    - Use functional and declarative programming patterns; avoid classes.
    - Favor iteration and modularization over code duplication.
    - Use descriptive variable names with auxiliary verbs (e.g., `isLoading`, `hasError`).
    - Structure files with exported components, subcomponents, helpers, static content, and types.
    - Use lowercase with dashes for directory names (e.g., `components/auth-wizard`).

    ### Optimization and Best Practices
    - Minimize the use of `'use client'`, `useEffect`, and `setState`; favor React Server Components (RSC) and Next.js SSR features.
    - Implement dynamic imports for code splitting and optimization.
    - Use responsive design with a mobile-first approach.
    - Optimize images: use WebP format, include size data, implement lazy loading.

    ### Error Handling and Validation
    - Prioritize error handling and edge cases:
      - Use early returns for error conditions.
      - Implement guard clauses to handle preconditions and invalid states early.
      - Use custom error types for consistent error handling.

    ### UI and Styling
    - Use modern UI frameworks (e.g., Tailwind CSS, Shadcn UI, Radix UI) for styling.
    - Implement consistent design and responsive patterns across platforms.

    ### State Management and Data Fetching
    - Use modern state management solutions (e.g., Zustand, TanStack React Query) to handle global state and data fetching.
    - Implement validation using Zod for schema validation.

    ### Security and Performance
    - Implement proper error handling, user input validation, and secure coding practices.
    - Follow performance optimization techniques, such as reducing load times and improving rendering efficiency.

    ### Testing and Documentation
    - Write unit tests for components using Jest and React Testing Library.
    - Provide clear and concise comments for complex logic.
    - Use JSDoc comments for functions and components to improve IDE intellisense.

    ### Methodology
    1. **System 2 Thinking**: Approach the problem with analytical rigor. Break down the requirements into smaller, manageable parts and thoroughly consider each step before implementation.
    2. **Tree of Thoughts**: Evaluate multiple possible solutions and their consequences. Use a structured approach to explore different paths and select the optimal one.
    3. **Iterative Refinement**: Before finalizing the code, consider improvements, edge cases, and optimizations. Iterate through potential enhancements to ensure the final solution is robust.

    **Process**:
    1. **Deep Dive Analysis**: Begin by conducting a thorough analysis of the task at hand, considering the technical requirements and constraints.
    2. **Planning**: Develop a clear plan that outlines the architectural structure and flow of the solution, using <PLANNING> tags if necessary.
    3. **Implementation**: Implement the solution step-by-step, ensuring that each part adheres to the specified best practices.
    4. **Review and Optimize**: Perform a review of the code, looking for areas of potential optimization and improvement.
    5. **Finalization**: Finalize the code by ensuring it meets all requirements, is secure, and is performant.
    
    Whit React
    This comprehensive guide outlines best practices, conventions, and standards for development with modern web technologies including ReactJS, NextJS, Redux, TypeScript, JavaScript, HTML, CSS, and UI frameworks.

    Development Philosophy
    - Write clean, maintainable, and scalable code
    - Follow SOLID principles
    - Prefer functional and declarative programming patterns over imperative
    - Emphasize type safety and static analysis
    - Practice component-driven development

    Code Implementation Guidelines
    Planning Phase
    - Begin with step-by-step planning
    - Write detailed pseudocode before implementation
    - Document component architecture and data flow
    - Consider edge cases and error scenarios

    Code Style
    - Use tabs for indentation
    - Use single quotes for strings (except to avoid escaping)
    - Omit semicolons (unless required for disambiguation)
    - Eliminate unused variables
    - Add space after keywords
    - Add space before function declaration parentheses
    - Always use strict equality (===) instead of loose equality (==)
    - Space infix operators
    - Add space after commas
    - Keep else statements on the same line as closing curly braces
    - Use curly braces for multi-line if statements
    - Always handle error parameters in callbacks
    - Limit line length to 80 characters
    - Use trailing commas in multiline object/array literals

    Naming Conventions
    General Rules
    - Use PascalCase for:
      - Components
      - Type definitions
      - Interfaces
    - Use kebab-case for:
      - Directory names (e.g., components/auth-wizard)
      - File names (e.g., user-profile.tsx)
    - Use camelCase for:
      - Variables
      - Functions
      - Methods
      - Hooks
      - Properties
      - Props
    - Use UPPERCASE for:
      - Environment variables
      - Constants
      - Global configurations

    Specific Naming Patterns
    - Prefix event handlers with 'handle': handleClick, handleSubmit
    - Prefix boolean variables with verbs: isLoading, hasError, canSubmit
    - Prefix custom hooks with 'use': useAuth, useForm
    - Use complete words over abbreviations except for:
      - err (error)
      - req (request)
      - res (response)
      - props (properties)
      - ref (reference)

    React Best Practices
    Component Architecture
    - Use functional components with TypeScript interfaces
    - Define components using the function keyword
    - Extract reusable logic into custom hooks
    - Implement proper component composition
    - Use React.memo() strategically for performance
    - Implement proper cleanup in useEffect hooks

    React Performance Optimization
    - Use useCallback for memoizing callback functions
    - Implement useMemo for expensive computations
    - Avoid inline function definitions in JSX
    - Implement code splitting using dynamic imports
    - Implement proper key props in lists (avoid using index as key)

    Next.js Best Practices
    Core Concepts
    - Utilize App Router for routing
    - Implement proper metadata management
    - Use proper caching strategies
    - Implement proper error boundaries

    Components and Features
    - Use Next.js built-in components:
      - Image component for optimized images
      - Link component for client-side navigation
      - Script component for external scripts
      - Head component for metadata
    - Implement proper loading states
    - Use proper data fetching methods

    Server Components
    - Default to Server Components
    - Use URL query parameters for data fetching and server state management
    - Use 'use client' directive only when necessary:
      - Event listeners
      - Browser APIs
      - State management
      - Client-side-only libraries

    TypeScript Implementation
    - Enable strict mode
    - Define clear interfaces for component props, state, and Redux state structure.
    - Use type guards to handle potential undefined or null values safely.
    - Apply generics to functions, actions, and slices where type flexibility is needed.
    - Utilize TypeScript utility types (Partial, Pick, Omit) for cleaner and reusable code.
    - Prefer interface over type for defining object structures, especially when extending.
    - Use mapped types for creating variations of existing types dynamically.

    UI and Styling
    Component Libraries
    - Use Shadcn UI for consistent, accessible component design.
    - Integrate Radix UI primitives for customizable, accessible UI elements.
    - Apply composition patterns to create modular, reusable components.

    Styling Guidelines
    - Use Tailwind CSS for styling
    - Use Tailwind CSS for utility-first, maintainable styling.
    - Design with mobile-first, responsive principles for flexibility across devices.
    - Implement dark mode using CSS variables or Tailwind’s dark mode features.
    - Ensure color contrast ratios meet accessibility standards for readability.
    - Maintain consistent spacing values to establish visual harmony.
    - Define CSS variables for theme colors and spacing to support easy theming and maintainability.

    State Management
    Local State
    - Use useState for component-level state
    - Implement useReducer for complex state
    - Use useContext for shared state
    - Implement proper state initialization

    Global State
    - Use Redux Toolkit for global state
    - Use createSlice to define state, reducers, and actions together.
    - Avoid using createReducer and createAction unless necessary.
    - Normalize state structure to avoid deeply nested data.
    - Use selectors to encapsulate state access.
    - Avoid large, all-encompassing slices; separate concerns by feature.


    Error Handling and Validation
    Form Validation
    - Use Zod for schema validation
    - Implement proper error messages
    - Use proper form libraries (e.g., React Hook Form)

    Error Boundaries
    - Use error boundaries to catch and handle errors in React component trees gracefully.
    - Log caught errors to an external service (e.g., Sentry) for tracking and debugging.
    - Design user-friendly fallback UIs to display when errors occur, keeping users informed without breaking the app.

    Testing
    Unit Testing
    - Write thorough unit tests to validate individual functions and components.
    - Use Jest and React Testing Library for reliable and efficient testing of React components.
    - Follow patterns like Arrange-Act-Assert to ensure clarity and consistency in tests.
    - Mock external dependencies and API calls to isolate unit tests.

    Integration Testing
    - Focus on user workflows to ensure app functionality.
    - Set up and tear down test environments properly to maintain test independence.
    - Use snapshot testing selectively to catch unintended UI changes without over-relying on it.
    - Leverage testing utilities (e.g., screen in RTL) for cleaner and more readable tests.

    Accessibility (a11y)
    Core Requirements
    - Use semantic HTML for meaningful structure.
    - Apply accurate ARIA attributes where needed.
    - Ensure full keyboard navigation support.
    - Manage focus order and visibility effectively.
    - Maintain accessible color contrast ratios.
    - Follow a logical heading hierarchy.
    - Make all interactive elements accessible.
    - Provide clear and accessible error feedback.

    Security
    - Implement input sanitization to prevent XSS attacks.
    - Use DOMPurify for sanitizing HTML content.
    - Use proper authentication methods.

    Internationalization (i18n)
    - Use next-i18next for translations
    - Implement proper locale detection
    - Use proper number and date formatting
    - Implement proper RTL support
    - Use proper currency formatting

    Documentation
    - Use JSDoc for documentation
    - Document all public functions, classes, methods, and interfaces
    - Add examples when appropriate
    - Use complete sentences with proper punctuation
    - Keep descriptions clear and concise
    - Use proper markdown formatting
    - Use proper code blocks
    - Use proper links
    - Use proper headings
    - Use proper lists