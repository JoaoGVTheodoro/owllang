# OwlLang Compiler - MVP

## Escolha da Linguagem: Python

**Por que Python?**

1. **Prototipagem rápida** - Foco em clareza, não performance
2. **Sem compilação** - Iteração imediata durante desenvolvimento
3. **Estruturas de dados expressivas** - Dataclasses para AST
4. **Biblioteca padrão rica** - Regex, enum, etc. já disponíveis
5. **Meta-circular** - Compilador em Python gerando Python (didático)

Para produção, migraríamos para Rust. Para MVP educacional, Python é ideal.

## Arquitetura

```
hello.owl
    │
    ▼
┌─────────────────┐
│     Lexer       │  Código fonte → Tokens
│  (lexer.py)     │
└────────┬────────┘
         │ List[Token]
         ▼
┌─────────────────┐
│     Parser      │  Tokens → AST
│  (parser.py)    │
└────────┬────────┘
         │ AST (Program)
         ▼
┌─────────────────┐
│   Transpiler    │  AST → Python source
│ (transpiler.py) │
└────────┬────────┘
         │ String (Python code)
         ▼
    hello.py
```

## Uso

```bash
# Transpilar arquivo
python -m owl compile hello.owl

# Transpilar e executar
python -m owl run hello.owl

# REPL (futuro)
python -m owl repl
```

## Escopo do MVP

### ✅ Suportado
- `let` (variáveis imutáveis)
- Literais: `Int`, `Float`, `String`, `Bool`
- Funções (`fn`)
- Chamadas de função
- `print()`
- `from python import ...`
- Operadores: `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `>`, `<=`, `>=`
- Comentários (`//`)

### ❌ Fora do escopo
- Classes, Structs, Enums
- Pattern matching
- Option/Result
- Async/Await
- Generics
- Type checking
