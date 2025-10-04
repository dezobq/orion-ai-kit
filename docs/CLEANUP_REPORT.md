# 🧹 Relatório de Limpeza - Orion AI Kit
**Data:** Outubro 2025
**Análise:** Repositório completo após evolução Blueprint v5.2

---

## 📊 Análise do Repositório

### Estrutura Atual (Antes da Limpeza)

```
orion-ai-kit/
├── docs/
│   ├── Blueprint_ Workflow Padrão...pdf (107KB) ❌ DEPRECADO
│   ├── blueprint-v2.md (26KB) ❌ DEPRECADO
│   ├── blueprint-v5.1-final.md (33KB) ❌ DEPRECADO
│   ├── blueprint-v5.2-production-ready.md (40KB) ✅ ATUAL
│   ├── gold.jsonl (315B) ✅ RAG eval
│   ├── qs.jsonl (262B) ✅ RAG eval
│   └── rag_queries.md (7.5KB) ✅ Documentação
│
├── Root/
│   ├── nul (2.2KB) ❌ LIXO (ping output)
│   ├── ai_cli.py.bak (4.4KB) ❌ BACKUP desnecessário
│   ├── blueprint-v2.md (26KB) ❌ DUPLICADO (está em docs/)
│   ├── __pycache__/ ❌ Cache Python (git ignora mas existe)
│   └── .stryker-tmp/ (3.0MB) ❌ TEMP mutation testing
│
├── Scripts/ ✅
│   ├── ai_post_pr.sh
│   ├── ai_pre_pr.sh
│   ├── check_thresholds.py
│   ├── eval_rag.py
│   ├── generate_summary.py
│   └── ingest_to_opensearch.py
│
├── Core/ ✅
│   ├── ai_cli.py
│   ├── CLAUDE.md
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── package.json
│
└── Config/ ✅
    ├── .github/workflows/
    ├── .claude/settings.json
    ├── codecov.yml
    ├── sonar-project.properties
    └── stryker.conf.json
```

---

## 🗑️ Arquivos para Remover

### 1. Lixo Acidental
- ❌ **nul** (2.2KB) - Saída acidental de comando ping
- ❌ **ai_cli.py.bak** (4.4KB) - Backup manual desnecessário

### 2. Temporários
- ❌ **.stryker-tmp/** (3.0MB) - Sandboxes de mutation testing
- ❌ **__pycache__/** - Bytecode Python compilado

### 3. Blueprints Deprecados
- ❌ **docs/Blueprint_ Workflow Padrão...pdf** (107KB) - Versão antiga PDF
- ❌ **docs/blueprint-v2.md** (26KB) - Superado por v5.2
- ❌ **docs/blueprint-v5.1-final.md** (33KB) - Tinha gaps críticos
- ❌ **blueprint-v2.md** (raiz) (26KB) - Duplicado de docs/

### 4. Manter (Histórico)
- ✅ **docs/blueprint-v5.2-production-ready.md** - VERSÃO ATUAL
- ✅ Mover blueprints antigos para `docs/archive/` (opcional)

---

## 📦 Espaço Recuperado

| Categoria | Arquivos | Tamanho |
|-----------|----------|---------|
| Lixo | 2 arquivos | 6.6 KB |
| Temporários | 2 diretórios | ~3.5 MB |
| Blueprints deprecados | 4 arquivos | 192 KB |
| **TOTAL** | **8 items** | **~3.7 MB** |

---

## 🔧 Ações de Limpeza

### 1. Remover Lixo
```bash
rm nul
rm ai_cli.py.bak
```

### 2. Limpar Temporários
```bash
rm -rf .stryker-tmp/
rm -rf __pycache__/
```

### 3. Organizar Blueprints

**Opção A: Deletar tudo (recomendado)**
```bash
cd docs/
rm "Blueprint_ Workflow Padrão P_ Coding Agents — Context Engineering + Rag + Reranker (1).pdf"
rm blueprint-v2.md
rm blueprint-v5.1-final.md
cd ..
rm blueprint-v2.md
```

**Opção B: Arquivar para histórico**
```bash
mkdir -p docs/archive/
mv docs/blueprint-v2.md docs/archive/
mv docs/blueprint-v5.1-final.md docs/archive/
mv docs/"Blueprint_ Workflow Padrão"*.pdf docs/archive/
rm blueprint-v2.md  # Duplicado na raiz
```

### 4. Atualizar .gitignore
```bash
# Adicionar ao .gitignore
echo "" >> .gitignore
echo "# Temporários" >> .gitignore
echo ".stryker-tmp/" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "*.bak" >> .gitignore
echo "nul" >> .gitignore
echo "" >> .gitignore
echo "# Blueprints deprecados (manter só em docs/)" >> .gitignore
echo "blueprint-*.md" >> .gitignore
```

---

## ✅ Estrutura Final (Após Limpeza)

```
orion-ai-kit/
├── docs/
│   ├── blueprint-v5.2-production-ready.md ✅ ÚNICO blueprint
│   ├── gold.jsonl ✅
│   ├── qs.jsonl ✅
│   ├── rag_queries.md ✅
│   └── archive/ (opcional)
│       ├── blueprint-v2.md
│       ├── blueprint-v5.1-final.md
│       └── Blueprint_Workflow.pdf
│
├── scripts/ ✅ (6 scripts Python/Bash)
├── .github/ ✅ (workflows CI/CD)
├── .claude/ ✅ (settings)
├── adapters/ ✅
├── memory/ ✅
├── prompts/ ✅
│
└── Core files ✅
    ├── ai_cli.py
    ├── CLAUDE.md
    ├── docker-compose.yml
    ├── Dockerfile
    ├── package.json
    └── etc.
```

---

## 🎯 Recomendação

### Ação Imediata (Opção A - Limpar tudo)
1. ✅ Deletar lixo (nul, .bak)
2. ✅ Deletar temporários (.stryker-tmp, __pycache__)
3. ✅ Deletar blueprints deprecados
4. ✅ Manter APENAS blueprint-v5.2-production-ready.md
5. ✅ Atualizar .gitignore

**Benefício:** Repositório limpo, -3.7MB, sem confusão

### Ação Conservadora (Opção B - Arquivar)
1. ✅ Deletar lixo
2. ✅ Deletar temporários
3. ✅ Mover blueprints antigos para docs/archive/
4. ✅ Atualizar .gitignore

**Benefício:** Histórico preservado, ainda recupera ~3.5MB

---

## 🚀 Próximos Passos

Após limpeza:
1. Commit mudanças: `git add -A && git commit -m "chore: cleanup deprecated files and temp directories"`
2. Verificar: `git status` (deve estar limpo)
3. Push: `git push origin main`

---

## 📋 Checklist de Limpeza

- [ ] Remover `nul`
- [ ] Remover `ai_cli.py.bak`
- [ ] Remover `blueprint-v2.md` (raiz)
- [ ] Limpar `.stryker-tmp/`
- [ ] Limpar `__pycache__/`
- [ ] Decidir: Deletar ou arquivar blueprints antigos
- [ ] Atualizar `.gitignore`
- [ ] Commit + push

---

**Conclusão:** Repositório tem ~3.7MB de arquivos desnecessários. Limpeza recomendada antes de implementar Blueprint v5.2.
