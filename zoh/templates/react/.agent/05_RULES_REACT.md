# .agent/05_RULES_REACT.md
# React Coding Rules & Standards

## 1. Component Structure
- Use Functional Components with Hooks.
- One component per file (prefer `index.tsx` within a folder if there are many sub-components).
- Name components using PascalCase (e.g., `UserProfile.tsx`).

## 2. State Management
- Use `useState` for local state.
- Use `useContext` or a global state manager (Redux, Zustand) for shared state.
- Keep state as close to the usage as possible.

## 3. Hooks
- Custom hooks must start with `use` prefix.
- All dependencies must be listed in `useEffect` and `useCallback`.

## 4. UI/UX
- Use TailwindCSS (if specified) or Vanilla CSS modules.
- Ensure 100% accessibility (aria labels, role).

## 5. Testing
- Use Vitest/Jest and React Testing Library.
- Every major component must have a `.test.tsx` file.
