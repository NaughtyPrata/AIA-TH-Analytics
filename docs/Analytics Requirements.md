### Current format (For each metric: rating from 1-5 & the explanation)

graph TD
    %% Categories
    subgraph Product_Pitch[Product Pitch]
        A1[Explain benefits of insurance]
        A2[Explain product details]
        A3[Answer product questions]
        A4[Close conversation with next appointment or sale]
        A5[Final Feedback]
    end

    subgraph Objection_Handling[Objection Handling]
        B1[Listening to objections]
        B2[Acknowledging objections]
        B3[Defusing objections]
        B4[Refocusing the customer]
        B5[Final Feedback]
    end

    subgraph Communication_Skills[Communication Skills]
        C1[Small Talk]
        C2[Content organisation]
        C3[Building rapport]
        C4[Give relevant examples]
        C5[Active listening]
        C6[Closing]
        C7[Final Feedback]
    end
### Statistical Analyses we can do with the current format:

### 1. **Descriptive Statistics (Per Metric and Category)**

**Purpose**: Understand overall performance distribution

**Metrics**: Mean, Median, Std Dev, Min/Max for each metric

### 🧪 Example:

| Metric | Mean | Median | Min | Max | Std Dev |
| --- | --- | --- | --- | --- | --- |
| Explain benefits | 4.1 | 4 | 2 | 5 | 0.8 |
| Defusing objections | 2.7 | 3 | 1 | 5 | 1.1 |
| Building rapport | 3.6 | 4 | 2 | 5 | 0.7 |

> Client Insight: “Agents are strong in explaining benefits but need help defusing objections.”
> 

### 2. **Category-Level Aggregation & Comparison**

**Purpose**: Identify strong vs. weak skill areas across agents

**Method**: Average score per category, compare across groups

### 🧪 Example:

| Category | Avg Score |
| --- | --- |
| Product Pitch | 3.9 |
| Objection Handling | 3.1 |
| Communication Skills | 3.6 |

> Client Insight: “Objection Handling is the weakest area and needs targeted improvement.”
> 

### 3. **Radar Charts or Heatmaps**

**Purpose**: Visualize strengths/weaknesses per agent or session

**Benefit**: Intuitive at-a-glance view for clients and trainers

### 4. **Inter-Metric Correlation Analysis**

**Purpose**: To understand how different behaviors or skills relate to one another. This helps identify if improving one area might lead to improvements in another.

**Method:** Use **Pearson** or **Spearman correlation** to compute a **correlation matrix** between all behaviour metrics.

- **Pearson**: Measures **linear** correlation.
- **Spearman**: Measures **monotonic** correlation (more robust to outliers and non-linear relationships). It uses **rank-order** rather than raw values.

### 🧪 Example (Spearman Correlation Matrix):

|  | Rapport | Defuse Obj | Small Talk | Refocus |
| --- | --- | --- | --- | --- |
| Rapport | 1.00 | **0.65** | 0.58 | 0.51 |
| Defusing Objections | 0.65 | 1.00 | 0.39 | 0.47 |
| Small Talk | 0.58 | 0.39 | 1.00 | 0.30 |
| Refocus | 0.51 | 0.47 | 0.30 | 1.00 |

> Client Insight: “Rapport and objection defusing are positively correlated. Improving rapport may improve objection handling too.”
> 

### 5. **Agent Performance Clustering**

**Purpose**: Segment agents into groups like 'pitchers', 'listeners', 'balanced'

**Method**: K-means clustering on metric scores

### 🧪 Example:

Cluster 1 – “Pitch Pros” (high Product Pitch scores)

Cluster 2 – “Empathetic Listeners” (high rapport & listening, low product details)

Cluster 3 – “Well-rounded” (high scores across categories)

| Cluster | Product Pitch | Rapport | Listening | Refocus |
| --- | --- | --- | --- | --- |
| 0 ("Pitch Pros") | 0.85 | 0.45 | 0.5 | 0.6 |
| 1 ("Empathetic Listeners") | 0.35 | 0.9 | 0.88 | 0.75 |
| 2 ("Well-rounded") | 0.75 | 0.75 | 0.8 | 0.8 |

This means a large portion of agents fall into a cluster with high **Product Pitch**, but lower **Rapport and Listening** scores. So, rather than training them more on content, focus on **emotional skills**

like empathy, turn-taking, active listening.

> Client Insight: “Half the agents are strong at explaining, but weak in communication — training can focus on emotional intelligence.”
> 

### 6. **Trend Analysis Over Time**

**If data is longitudinal per agent**, track improvement

### 🧪 Example:

| Agent | Session 1 | Session 2 | Session 3 | Trend |
| --- | --- | --- | --- | --- |
| A | 3.2 | 3.7 | 4.0 | 📈 Upward |
| B | 4.1 | 3.9 | 3.6 | 📉 Downward |
| C | 2.8 | 2.8 | 2.9 | ➖ Flat |

> Client Insight: “Agent A is improving steadily; Agent B is declining and may need follow-up.”
> 

### 7. **Session Variability Index (proto-consistency score)**

**Purpose**: Assess performance stability

**Method**: Calculate standard deviation across sessions for each agent

**Session Variability Index (SVI)** measures how **stable or inconsistent** an agent’s performance is across multiple sessions using the standard deviation of their scores.

### Why it's valuable:

- High average score is **not enough** — clients also care about **reliability**.
- Consistent agents are more dependable in real-world deployment.
- Helps flag erratic performance, fatigue issues, or areas for coaching.

## How to Calculate the Session Variability Index

### Step-by-step:

Let's say each agent completes multiple sessions. For each session, you collect a score (either overall or by category).

### Step 1: Get scores for each session

Example: Agent A's total session scores (average of all metrics per session)

| Session | Score |
| --- | --- |
| 1 | 3.5 |
| 2 | 3.8 |
| 3 | 3.9 |
| 4 | 4.0 |
| 5 | 3.7 |

### Step 2: Calculate the standard deviation (SD)

$$

\text{Mean} = \frac{3.5 + 3.8 + 3.9 + 4.0 + 3.7}{5} = 3.78

$$

$$
\text{SD} = \sqrt{\frac{(3.5 - 3.78)^2 + (3.8 - 3.78)^2 + (3.9 - 3.78)^2 + (4.0 - 3.78)^2 + (3.7 - 3.78)^2}{5}} \approx 0.17
$$

So, **SVI for Agent A = 0.17**

---

## 🎯 Interpretation

| SVI Range | Meaning | Client Recommendation |
| --- | --- | --- |
| **0.0 – 0.3** | Very consistent | Reliable, steady performer |
| **0.3 – 0.6** | Some variation | Acceptable, but may benefit from coaching |
| **> 0.6** | High inconsistency | Unstable performance — requires investigation |

> Pro tip: You can compute SVI per category (e.g., Objection Handling only) to isolate inconsistent skill areas.
> 

---

## 🧠 Advanced Usage

- **Compare SVI vs. average score**
    
    A high scorer with high variability may be overconfident or inconsistent under pressure.
    
- **Visualize with control charts**
    
    Use line graphs with mean ± 1 SD bands to see if performance stays in control.
    
- **Normalize SVI by difficulty**
    
    If some sessions are harder than others (e.g., tougher objection scripts), adjust for this.
    

---

## 🧪 Example Agent Comparison

| Agent | Avg Score | SVI (Std Dev) | Notes |
| --- | --- | --- | --- |
| A | 4.0 | **0.15** | Consistent & high-performing |
| B | 4.2 | **0.65** | High performer but very erratic |
| C | 3.5 | **0.25** | Moderate but reliable |

> Client Insight: “Agent B looks good on paper but is unstable — coaching needed for consistency.”
> 

### 🧪 Example:

| Agent | Std Dev (All Metrics) | Interpretation |
| --- | --- | --- |
| A | 0.5 | Consistent performance |
| B | 1.3 | Highly inconsistent; unstable |
| C | 0.2 | Very stable agent |

> Client Insight: “Agent B is erratic; investigate if scenario complexity or fatigue is a factor.”
> 

### 8. **Success Driver Identification (if you define outcome) - this will need bigger dataset approx >100, if lesser do not use this. will result in overfitting & bias results**

**Purpose**: Find what metrics lead to success

**Method**: Regression or decision trees if you define a binary outcome like “sale” or “appointment”

Assuming you mark each session as **Success (1)** or **Fail (0)**.

For more reliable p-values and confidence intervals: **100+** data points is better.

### 🧪 Regression Output Example:

```

Success = 0.2 + (0.6 × Defusing Objections) + (0.4 × Rapport)

```

> Client Insight: “Defusing objections is the strongest predictor of session success.”
> 

## 🎯 Additional Visual to Use

| Type | Example Description |
| --- | --- |
| **Radar Chart** | Visualize skill balance for each agent or average team profile |
| **Boxplots** | Show spread of scores per metric (e.g., some metrics have wide variance) |
| **Heatmap** | Grid of agents vs metrics, colored by score for easy scan |
| **Line Chart** | Session-over-session score progression per agent or per category |

## 🧩 **Comprehensive Evaluation Metrics Framework**

| **Category** | **Metric** | **Description / Purpose** |
| --- | --- | --- |
| 🟩 **Product Pitch** | Explain benefits of insurance | Clarity and relevance of conveyed benefits |
|  | Explain product details | Accuracy and completeness of product explanation |
|  | Answer product questions | Confidence and correctness of responses |
|  | Close with appointment/sale | Whether agent successfully ends with a next step |
| 🟪 **Objection Handling** | Listening to objections | Active listening skills |
|  | Acknowledging objections | Shows understanding and empathy |
|  | Defusing objections | Uses logic, data, or empathy to neutralize concerns |
|  | Refocusing the customer | Redirects the conversation toward value/sale |
| 🟧 **Communication Skills** | Small talk | Naturalness and appropriateness of introductory conversation |
|  | Content organisation | Logical and clear flow of ideas |
|  | Building rapport | Warmth, empathy, and trust-building |
|  | Give relevant examples | Realistic, persuasive use of analogies or scenarios |
|  | Active listening | Detects and responds appropriately to cues |
|  | Closing | Summarizes and ends effectively |
| 🧠 **Pattern Recognition** | Intent match accuracy | Correctly identifying the avatar’s scenario or objection type |
|  | Script adherence score | Matching expected script structure or decision paths |
|  | Keyword coverage | % of required/critical terms hit in the pitch |
|  | Avatar cue alignment | Picks up on subtle prompts from avatar (e.g., hesitation cues) |
| 🔁 **Performance Consistency** | Stability index across sessions | (max - min) / avg across sessions for a given metric |
|  | Score standard deviation | Spread of scores across multiple attempts |
|  | Resilience to traps or complexity | Performance drop when avatar introduces harder objections |
| 🧪 **Efficiency & Delivery** | Talk-to-listen ratio | Speaking vs. listening balance |
|  | Response latency | How fast agent reacts to prompts |
|  | Word count per response | Indicator of verbosity or conciseness |
|  | Redundancy score | Measures unnecessary repetition |
| 🎯 **Outcome Simulation** | Simulated conversion success | Whether avatar would agree to appointment/sale |
|  | Test objection response accuracy | Predefined test objections handled correctly |
|  | Calibration score | Degree of alignment to "ideal" response profile |
| 💬 **Language Use Metrics** | Confidence index | Frequency of hedging language (e.g., "maybe", "I think") |
|  | Language clarity score | Readability and lack of jargon (if text-based) |