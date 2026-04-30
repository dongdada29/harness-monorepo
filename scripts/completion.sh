#!/bin/bash
# completion.sh — harness CLI shell completion (bash + zsh)
# Usage: source <(bash completion.sh)   # for current session
#   or: cp completion.sh /etc/bash_completion.d/harness  # system-wide bash
#   or: autoload -Uz compinit && compinit  # zsh: move to ~/.zsh/completion/

_harness_completions() {
  local cur prev words cword
  _get_comp_words_by_ref cur prev words cword

  local commands="init benchmark test state verify heal healing open-pr clean doctor log diff score"
  local state_cmds="start done blocked gate show cp history"
  local healing_cmds="on off status"
  local init_templates="basic advanced generic package"
  local init_types="generic nuwax electron"
  local gate_statuses="passed failed pending"

  # No completion yet — suggest commands
  if [[ $cword -eq 1 ]]; then
    COMPREPLY=($(compgen -W "$commands" -- "$cur"))
    return
  fi

  local cmd="${words[1]}"

  # harness state <subcmd>
  if [[ "$cmd" == "state" ]]; then
    if [[ $cword -eq 2 ]]; then
      COMPREPLY=($(compgen -W "$state_cmds" -- "$cur"))
    elif [[ "$prev" == "start" || "$prev" == "done" || "$prev" == "blocked" ]]; then
      return  # task description — no completion
    elif [[ "$prev" == "gate" ]]; then
      COMPREPLY=($(compgen -W "$gate_statuses" -- "$cur"))
    elif [[ "$prev" == "cp" ]]; then
      COMPREPLY=($(compgen -W "CP0 CP1 CP2 CP3 CP4" -- "$cur"))
    fi
    return
  fi

  # harness heal [project-dir] [--dry-run|--force]
  if [[ "$cmd" == "heal" ]]; then
    COMPREPLY=($(compgen -W "--dry-run --force" -- "$cur"))
    return
  fi

  # harness init <type> <target-dir> [--template]
  if [[ "$cmd" == "init" ]]; then
    if [[ $cword -eq 2 ]]; then
      COMPREPLY=($(compgen -W "$init_types" -- "$cur"))
    elif [[ "$prev" == "--template" || "$prev" == "-t" ]]; then
      COMPREPLY=($(compgen -W "$init_templates" -- "$cur"))
    fi
    return
  fi

  # harness healing <on|off|status>
  if [[ "$cmd" == "healing" ]]; then
    COMPREPLY=($(compgen -W "$healing_cmds" -- "$cur"))
    return
  fi

  # harness benchmark|test|verify|doctor|score [project-dir]
  # harness open-pr [args...]
  # harness clean [target-dir]
  # harness log [target-dir] [-n|--limit]
  # harness diff [project-dir] [cp]

  COMPREPLY=($(compgen -W "--help -h" -- "$cur"))
}

# Install for bash
if [[ -n "$BASH_VERSION" ]]; then
  complete -F _harness_completions harness
fi

# Install for zsh (only when running in zsh)
if [[ -n "$ZSH_VERSION" ]]; then
  # shellcheck disable=SC2034
  compdef _harness_completions harness 2>/dev/null
fi

echo "Harness completion loaded (bash + zsh)"
