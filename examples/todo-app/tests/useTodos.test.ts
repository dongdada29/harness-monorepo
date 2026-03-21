// useTodos Hook 测试

import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useTodos } from '../src/hooks/useTodos';

describe('useTodos', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should initialize with empty todos', () => {
    const { result } = renderHook(() => useTodos());
    
    expect(result.current.todos).toEqual([]);
    expect(result.current.total).toBe(0);
    expect(result.current.active).toBe(0);
    expect(result.current.completed).toBe(0);
  });

  it('should add a todo', () => {
    const { result } = renderHook(() => useTodos());
    
    act(() => {
      result.current.addTodo('Test todo');
    });

    expect(result.current.todos).toHaveLength(1);
    expect(result.current.todos[0].text).toBe('Test todo');
    expect(result.current.todos[0].completed).toBe(false);
    expect(result.current.total).toBe(1);
    expect(result.current.active).toBe(1);
  });

  it('should toggle a todo', () => {
    const { result } = renderHook(() => useTodos());
    
    act(() => {
      result.current.addTodo('Test todo');
    });

    const todoId = result.current.todos[0].id;

    act(() => {
      result.current.toggleTodo(todoId);
    });

    expect(result.current.todos[0].completed).toBe(true);
    expect(result.current.completed).toBe(1);
    expect(result.current.active).toBe(0);
  });

  it('should delete a todo', () => {
    const { result } = renderHook(() => useTodos());
    
    act(() => {
      result.current.addTodo('Test todo');
    });

    const todoId = result.current.todos[0].id;

    act(() => {
      result.current.deleteTodo(todoId);
    });

    expect(result.current.todos).toHaveLength(0);
    expect(result.current.total).toBe(0);
  });

  it('should filter todos correctly', () => {
    const { result } = renderHook(() => useTodos());
    
    act(() => {
      result.current.addTodo('Active todo');
      result.current.addTodo('Completed todo');
    });

    const completedId = result.current.todos[1].id;

    act(() => {
      result.current.toggleTodo(completedId);
    });

    act(() => {
      result.current.setFilter('active');
    });
    expect(result.current.todos).toHaveLength(1);
    expect(result.current.todos[0].text).toBe('Active todo');

    act(() => {
      result.current.setFilter('completed');
    });
    expect(result.current.todos).toHaveLength(1);
    expect(result.current.todos[0].text).toBe('Completed todo');

    act(() => {
      result.current.setFilter('all');
    });
    expect(result.current.todos).toHaveLength(2);
  });

  it('should persist todos to localStorage', () => {
    const { result } = renderHook(() => useTodos());
    
    act(() => {
      result.current.addTodo('Test todo');
    });

    // 重新加载
    const { result: result2 } = renderHook(() => useTodos());
    expect(result2.current.todos).toHaveLength(1);
    expect(result2.current.todos[0].text).toBe('Test todo');
  });
});
