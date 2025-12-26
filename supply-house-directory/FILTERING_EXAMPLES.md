# Trade Filtering Examples - Using primaryTrade

This document demonstrates how the `primaryTrade` field improves trade filtering clarity and user experience.

## Problem: Before primaryTrade

When filtering for HVAC suppliers, users would see branches like:

```
Results for "HVAC Suppliers in Denver":
1. Baker Distributing – Englewood (HVAC specialist) ✓
2. Johnstone Supply – Denver (HVAC specialist) ✓
3. Ferguson - Denver (Plumbing/PVF & HVAC) ❓
4. Ferguson Plumbing Supply (North Denver) ❓
5. Rampart Supply – Denver ❓
6. United Refrigeration – Denver (HVAC specialist) ✓
```

**User Confusion:**
- "Why is 'Ferguson Plumbing Supply' showing up in HVAC results?"
- "Is Rampart Supply an HVAC or plumbing company?"
- Users waste time visiting plumbing-focused branches looking for HVAC products

## Solution: With primaryTrade

Applications can now offer **two filtering options**:

### Option 1: "HVAC Specialists" (Primary Focus)
Filter by `primaryTrade === 'HVAC'`

```javascript
const hvacSpecialists = branches.filter(b => 
  b.primaryTrade === 'HVAC' || 
  (b.trades.includes('HVAC') && b.trades.length === 1)
);
```

Results:
```
HVAC Specialists in Denver:
1. Baker Distributing – Englewood (HVAC only)
2. Johnstone Supply – Denver (HVAC only)
3. United Refrigeration – Denver (HVAC only)
4. Rampart Supply – Denver (HVAC primary, also Plumbing)
5. Ferguson Plumbing & HVAC Supply - Arvada (HVAC primary, also Plumbing)
```

### Option 2: "All HVAC Suppliers" (Any Coverage)
Filter by `trades.includes('HVAC')`

```javascript
const allHVACSuppliers = branches.filter(b => 
  b.trades.includes('HVAC')
);
```

Results:
```
All HVAC Suppliers in Denver:
1. Baker Distributing – Englewood (HVAC only)
2. Johnstone Supply – Denver (HVAC only)
3. United Refrigeration – Denver (HVAC only)
4. Rampart Supply – Denver (HVAC primary, also Plumbing)
5. Ferguson Plumbing & HVAC Supply - Arvada (HVAC primary, also Plumbing)
6. Ferguson - Denver (Plumbing primary, also HVAC)
7. Ferguson Plumbing Supply (North Denver) (Plumbing primary, also HVAC)
... (10 more Ferguson plumbing locations that carry some HVAC)
```

## UI/UX Recommendations

### 1. Default Filter: Primary Trade Only

By default, show only specialists and primary-focused branches:

```javascript
// Default HVAC filter
const defaultResults = branches.filter(b => 
  b.primaryTrade === 'HVAC' || 
  (b.trades.includes('HVAC') && !b.primaryTrade)
);
```

**Benefits:**
- Reduces noise in results
- Users see the most relevant branches first
- Fewer complaints about irrelevant results

### 2. Toggle for "Include Secondary"

Provide a checkbox or toggle:

```
☑ Show HVAC specialists only
☐ Include suppliers with HVAC as secondary trade
```

When toggled on, show all branches where `trades.includes('HVAC')`.

### 3. Visual Indicators

Use badges or icons to indicate primary vs. secondary:

```
Ferguson - Denver
  🟦 Plumbing  🟨 HVAC (secondary)

Rampart Supply – Denver
  🟦 HVAC  🟨 Plumbing (secondary)

Johnstone Supply – Denver
  🟦 HVAC
```

## Code Examples

### React Component Example

```jsx
function TradeFilter({ trade }) {
  const [includeSecondary, setIncludeSecondary] = useState(false);
  
  const filteredBranches = branches.filter(branch => {
    if (includeSecondary) {
      // Show all branches that serve this trade
      return branch.trades.includes(trade);
    } else {
      // Show only specialists and primary-focused branches
      return branch.primaryTrade === trade || 
             (branch.trades.includes(trade) && branch.trades.length === 1);
    }
  });
  
  return (
    <div>
      <h2>{trade} Suppliers</h2>
      <label>
        <input 
          type="checkbox" 
          checked={includeSecondary}
          onChange={(e) => setIncludeSecondary(e.target.checked)}
        />
        Include suppliers with {trade} as secondary trade
      </label>
      
      <div className="results">
        {filteredBranches.map(branch => (
          <BranchCard 
            key={branch.id} 
            branch={branch}
            isPrimary={branch.primaryTrade === trade}
          />
        ))}
      </div>
    </div>
  );
}

function BranchCard({ branch, isPrimary }) {
  return (
    <div className="branch-card">
      <h3>{branch.name}</h3>
      <div className="trades">
        {branch.trades.map(t => (
          <Badge 
            key={t}
            text={t}
            primary={t === branch.primaryTrade}
          />
        ))}
      </div>
    </div>
  );
}
```

### SQL Query Example

```sql
-- HVAC specialists only (primary focus)
SELECT * FROM branches 
WHERE primaryTrade = 'HVAC' 
   OR (trades LIKE '%HVAC%' AND trades NOT LIKE '%,%');

-- All HVAC suppliers (primary or secondary)
SELECT * FROM branches 
WHERE trades LIKE '%HVAC%';

-- Multi-trade branches with HVAC secondary
SELECT * FROM branches 
WHERE trades LIKE '%HVAC%' 
  AND primaryTrade != 'HVAC'
  AND primaryTrade IS NOT NULL;
```

## Search Ranking

Use `primaryTrade` to improve search result ranking:

```javascript
function rankBranches(branches, searchTrade) {
  return branches
    .filter(b => b.trades.includes(searchTrade))
    .map(b => ({
      ...b,
      score: calculateScore(b, searchTrade)
    }))
    .sort((a, b) => b.score - a.score);
}

function calculateScore(branch, searchTrade) {
  let score = 0;
  
  // Primary trade match: highest priority
  if (branch.primaryTrade === searchTrade) {
    score += 100;
  }
  
  // Single-trade specialist: high priority
  if (branch.trades.length === 1 && branch.trades.includes(searchTrade)) {
    score += 100;
  }
  
  // Multi-trade with secondary match: lower priority
  if (branch.trades.includes(searchTrade) && branch.primaryTrade !== searchTrade) {
    score += 50;
  }
  
  // Other factors (distance, rating, etc.)
  score += calculateOtherFactors(branch);
  
  return score;
}
```

## Analytics Use Cases

### 1. Market Coverage Analysis

```javascript
// How many HVAC specialists vs. multi-trade suppliers?
const hvacSpecialists = branches.filter(b => 
  b.trades.includes('HVAC') && b.trades.length === 1
).length;

const hvacPrimary = branches.filter(b => 
  b.primaryTrade === 'HVAC' && b.trades.length > 1
).length;

const hvacSecondary = branches.filter(b => 
  b.trades.includes('HVAC') && b.primaryTrade !== 'HVAC'
).length;

console.log(`HVAC Coverage:
  Specialists: ${hvacSpecialists}
  Primary Multi-Trade: ${hvacPrimary}
  Secondary Multi-Trade: ${hvacSecondary}
`);
```

### 2. Chain Business Model Analysis

```javascript
// Which chains are HVAC specialists vs. multi-trade?
const chainAnalysis = branches.reduce((acc, b) => {
  if (!acc[b.chain]) {
    acc[b.chain] = {
      hvacOnly: 0,
      plumbingOnly: 0,
      hvacPrimary: 0,
      plumbingPrimary: 0
    };
  }
  
  if (b.trades.length === 1) {
    if (b.trades[0] === 'HVAC') acc[b.chain].hvacOnly++;
    if (b.trades[0] === 'Plumbing') acc[b.chain].plumbingOnly++;
  } else {
    if (b.primaryTrade === 'HVAC') acc[b.chain].hvacPrimary++;
    if (b.primaryTrade === 'Plumbing') acc[b.chain].plumbingPrimary++;
  }
  
  return acc;
}, {});
```

## Benefits Summary

1. **Improved User Experience:**
   - Users find the most relevant branches faster
   - Less confusion about branch specialization
   - Clearer expectations before visiting

2. **Better Search Results:**
   - More accurate filtering
   - Improved result ranking
   - Reduced noise in results

3. **Business Intelligence:**
   - Understand market coverage by trade
   - Identify multi-trade vs. specialist patterns
   - Better competitive analysis

4. **Backward Compatibility:**
   - Applications not using `primaryTrade` continue to work
   - Progressive enhancement opportunity
   - No breaking changes to existing integrations

---

**Implementation Date:** 2025-12-26  
**Coverage:** 31 multi-trade branches in Colorado dataset  
**Next Steps:** Consider extending to other states as datasets are audited
