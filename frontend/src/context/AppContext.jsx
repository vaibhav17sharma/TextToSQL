import { createContext, useContext, useReducer } from 'react';

const AppContext = createContext();

const initialState = {
  connection: {
    isConnected: false,
    config: null,
    error: null,
    loading: false
  },
  schema: {
    tables: [],
    loading: false,
    error: null
  },
  chat: {
    messages: [],
    loading: false,
    error: null
  },
  history: []
};

function appReducer(state, action) {
  switch (action.type) {
    case 'SET_CONNECTION_LOADING':
      return {
        ...state,
        connection: { ...state.connection, loading: action.payload, error: null }
      };
    case 'SET_CONNECTION_SUCCESS':
      return {
        ...state,
        connection: {
          isConnected: true,
          config: action.payload,
          loading: false,
          error: null
        }
      };
    case 'SET_CONNECTION_ERROR':
      return {
        ...state,
        connection: {
          ...state.connection,
          loading: false,
          error: action.payload,
          isConnected: false
        }
      };
    case 'SET_SCHEMA_LOADING':
      return {
        ...state,
        schema: { ...state.schema, loading: action.payload }
      };
    case 'SET_SCHEMA_SUCCESS':
      return {
        ...state,
        schema: { tables: action.payload, loading: false, error: null }
      };
    case 'SET_SCHEMA_ERROR':
      return {
        ...state,
        schema: { ...state.schema, loading: false, error: action.payload }
      };
    case 'ADD_MESSAGE':
      return {
        ...state,
        chat: {
          ...state.chat,
          messages: [...state.chat.messages, action.payload]
        }
      };
    case 'SET_CHAT_LOADING':
      return {
        ...state,
        chat: { ...state.chat, loading: action.payload }
      };
    case 'SET_CHAT_ERROR':
      return {
        ...state,
        chat: { ...state.chat, loading: false, error: action.payload }
      };
    case 'ADD_TO_HISTORY':
      return {
        ...state,
        history: [action.payload, ...state.history.slice(0, 9)]
      };
    case 'CLEAR_CHAT':
      return {
        ...state,
        chat: { messages: [], loading: false, error: null }
      };
    case 'DISCONNECT_DATABASE':
      return {
        ...initialState
      };
    default:
      return state;
  }
}

export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppContext.Provider value={{ state, dispatch }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}