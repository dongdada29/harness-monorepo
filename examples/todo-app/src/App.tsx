// 主应用组件

import React from 'react';
import { TodoInput } from './components/TodoInput';
import { TodoList } from './components/TodoList';
import { useTodos } from './hooks/useTodos';
import './App.css';

function App() {
  const {
    todos,
    filter,
    setFilter,
    addTodo,
    toggleTodo,
    deleteTodo,
    total,
    active,
    completed,
  } = useTodos();

  return (
    <div className="app">
      <header>
        <h1>Todo App</h1>
        <p>harness-monorepo Example</p>
      </header>

      <main>
        <TodoInput onAdd={addTodo} />
        <TodoList
          todos={todos}
          filter={filter}
          onSetFilter={setFilter}
          onToggle={toggleTodo}
          onDelete={deleteTodo}
          total={total}
          active={active}
          completed={completed}
        />
      </main>
    </div>
  );
}

export default App;
