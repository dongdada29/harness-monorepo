// TodoList 组件

import React from 'react';
import { Todo, FilterType } from '../types/todo';
import { TodoItem } from './TodoItem';

interface TodoListProps {
  todos: Todo[];
  filter: FilterType;
  onSetFilter: (filter: FilterType) => void;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  total: number;
  active: number;
  completed: number;
}

export function TodoList({
  todos,
  filter,
  onSetFilter,
  onToggle,
  onDelete,
  total,
  active,
  completed,
}: TodoListProps) {
  return (
    <div className="todo-list">
      {/* Filter buttons */}
      <div className="filters">
        <button
          onClick={() => onSetFilter('all')}
          className={filter === 'all' ? 'active' : ''}
        >
          All ({total})
        </button>
        <button
          onClick={() => onSetFilter('active')}
          className={filter === 'active' ? 'active' : ''}
        >
          Active ({active})
        </button>
        <button
          onClick={() => onSetFilter('completed')}
          className={filter === 'completed' ? 'active' : ''}
        >
          Completed ({completed})
        </button>
      </div>

      {/* Todo list */}
      <ul className="todos">
        {todos.length === 0 ? (
          <li className="empty">No todos yet</li>
        ) : (
          todos.map(todo => (
            <TodoItem
              key={todo.id}
              todo={todo}
              onToggle={onToggle}
              onDelete={onDelete}
            />
          ))
        )}
      </ul>
    </div>
  );
}
