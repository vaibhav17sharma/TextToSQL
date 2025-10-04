# Text-to-SQL AI Assistant Frontend

A modern React frontend application for converting natural language queries to SQL using AI/ML.

## Features

- **Database Connection**: Connect via credentials or file upload
- **Schema Explorer**: Visual database schema exploration
- **Natural Language Queries**: Chat-like interface for SQL generation
- **Multi-turn Conversations**: Follow-up queries in context
- **Session History**: Navigate and rerun past queries
- **Real-time Results**: Display query results in formatted tables
- **Error Handling**: Graceful error messages and suggestions
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 19** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **Axios** - HTTP client
- **Context API** - State management

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or pnpm

### Installation

1. Install dependencies:
```bash
npm install
# or
pnpm install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
# or
pnpm dev
```

4. Open [http://localhost:5173](http://localhost:5173)

## Project Structure

```
src/
├── components/          # React components
│   ├── DatabaseConnection.jsx
│   ├── SchemaExplorer.jsx
│   ├── ChatInterface.jsx
│   └── SessionHistory.jsx
├── context/            # React context for state management
│   └── AppContext.jsx
├── services/           # API services and mocks
│   └── api.js
├── hooks/              # Custom React hooks
├── App.jsx             # Main application component
├── App.css             # Global styles
├── index.css           # Tailwind imports
└── main.jsx            # Application entry point
```

## API Integration

The application is designed to work with the following backend endpoints:

- `POST /api/connect-db` - Database connection
- `GET /api/schema` - Fetch database schema
- `POST /api/query` - Execute natural language query

Mock data is provided for development. Set `VITE_MOCK_API=false` to use real API endpoints.

## State Management

Uses React Context API with useReducer for:

- Database connection state
- Schema data
- Chat messages and history
- Loading states and errors

## Styling

- **Tailwind CSS** for utility-first styling
- **Responsive design** with mobile-first approach
- **Accessible** color contrast and focus states
- **Custom scrollbars** and animations

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Environment Variables

- `VITE_API_URL` - Backend API base URL
- `VITE_MOCK_API` - Enable/disable mock API responses

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Contributing

1. Follow the existing code style
2. Add proper error handling
3. Include loading states for async operations
4. Ensure responsive design
5. Add proper accessibility attributes