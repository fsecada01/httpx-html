# Refactor Plan - httpx-html Library

## Initial State Analysis

**Current Architecture**: 
- Well-structured HTML parsing library built on httpx
- Three main modules: `__init__.py`, `session.py`, `parse_.py`
- Follows object-oriented design with inheritance hierarchy
- Uses pyppeteer for JavaScript rendering capabilities

**Problem Areas Identified**:
1. **Code Duplication**: `render()` and `arender()` methods share 95% identical logic (parse_.py:659-771, 772-829)
2. **Complex Functions**: Render methods are 100+ lines with too many parameters (11 params each)
3. **Security Risk**: Use of `eval()` in cookie conversion (parse_.py:631)
4. **Inconsistent Browser Management**: Multiple `hasattr(self, "_browser")` checks scattered across session.py
5. **Large File**: `parse_.py` is 839 lines - should be split into focused modules
6. **Magic Numbers**: Hardcoded values like retries=8, timeout=8.0 scattered throughout
7. **Nested Functions**: Multiple nested function definitions that could be extracted

**Dependencies**: 
- httpx, pyppeteer, lxml, pyquery, beautifulsoup4
- No breaking changes to public API planned

**Test Coverage**: Basic tests exist in tests/ directory

## Refactoring Tasks (Prioritized by Risk/Impact)

### Phase 1: Safety & Security Fixes (High Priority)

1. **CRITICAL: Remove eval() Security Risk** ⚠️
   - File: `src/httpx_html/parse_.py:631`
   - Replace `eval(f"cookiejar.{key}")` with safe attribute access
   - Risk: High (security vulnerability)
   - Effort: Low

2. **Extract Configuration Constants**
   - Create `src/httpx_html/constants.py`
   - Move DEFAULT_* values and magic numbers
   - Risk: Low
   - Effort: Low

### Phase 2: Code Duplication Elimination (High Priority)

3. **Refactor Render Methods - Extract Common Logic**
   - Extract shared render logic into `_render_common()` method
   - Keep `render()` and `arender()` as thin wrappers
   - Reduce duplication from ~150 lines to ~30 lines
   - Risk: Medium (complex rendering logic)
   - Effort: Medium

4. **Create RenderConfig Dataclass**
   - Replace 11 render parameters with configuration object
   - Improve method signatures and maintainability
   - Risk: Low (backward compatible)
   - Effort: Low

### Phase 3: Structure Improvements (Medium Priority)

5. **Split parse_.py into Focused Modules**
   - `src/httpx_html/parsers/base.py` - BaseParser class
   - `src/httpx_html/parsers/element.py` - Element class
   - `src/httpx_html/parsers/html.py` - HTML class
   - `src/httpx_html/rendering/` - Browser rendering logic
   - Risk: Medium (import changes)
   - Effort: High

6. **Improve Browser Management**
   - Create `BrowserManager` class for consistent browser lifecycle
   - Eliminate scattered `hasattr(self, "_browser")` checks
   - Risk: Medium
   - Effort: Medium

7. **Extract Cookie Handling**
   - Move cookie conversion logic to separate `CookieHandler` class
   - Fix security issue and improve testability
   - Risk: Low
   - Effort: Medium

### Phase 4: API Improvements (Low Priority)

8. **Improve Error Handling**
   - Create custom exception hierarchy
   - Replace generic exceptions with specific ones
   - Risk: Low
   - Effort: Low

9. **Add Type Hints Validation**
   - Review and improve type annotations
   - Add mypy configuration
   - Risk: Low
   - Effort: Low

10. **Extract Utility Functions**
    - Move `_get_first_or_list()` and similar to utilities module
    - Risk: Low
    - Effort: Low

## Validation Checklist

- [ ] All old patterns removed
- [ ] No broken imports
- [ ] All tests passing
- [ ] Build successful 
- [ ] Type checking clean (add mypy)
- [ ] No orphaned code
- [ ] Documentation updated
- [ ] Security vulnerability (eval) eliminated
- [ ] No performance regression
- [ ] API backward compatibility maintained

## De-Para Mapping

| Before | After | Status |
|--------|-------|--------|
| `eval(f"cookiejar.{key}")` | `getattr(cookie, key, None)` | Pending |
| `render()` + `arender()` duplicated logic | `_render_common()` + thin wrappers | Pending |
| 11 render parameters | `RenderConfig` dataclass | Pending |
| 839-line `parse_.py` | Split into 4 focused modules | Pending |
| `hasattr(self, "_browser")` scattered | `BrowserManager` class | Pending |
| Cookie conversion in HTML class | `CookieHandler` class | Pending |

## Risk Assessment

**High Risk Changes**:
- Render method refactoring (core functionality)
- Module splitting (many imports affected)

**Medium Risk Changes**:
- Browser management refactoring
- Cookie handling extraction

**Low Risk Changes**:
- Configuration constants
- Error handling improvements
- Type hints

## Estimated Timeline

- **Phase 1**: 30 minutes
- **Phase 2**: 1.5 hours  
- **Phase 3**: 2 hours
- **Phase 4**: 1 hour

**Total**: ~5 hours of development + testing

## Rollback Strategy

1. Git commits at each logical checkpoint
2. Keep original code in comments during transition
3. Comprehensive test validation after each phase
4. Module-by-module rollback capability

## Success Metrics

- Reduce `parse_.py` from 839 to <300 lines
- Eliminate 95% code duplication in render methods
- Remove security vulnerability (eval usage)
- Maintain 100% API backward compatibility
- Improve test coverage to >90%