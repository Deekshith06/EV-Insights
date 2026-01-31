"""
IMPROVED EV ADVISOR - Research-Based Approach

Based on consumer behavior research, people choose cars through this decision hierarchy:

1. **Primary Non-Compensatory Filters** (Deal-breakers - applied first):
   - Budget/Price (55% cite as #1 factor)
   - Vehicle Type/Body Style (90%+ stay within same type)
   - Fuel Efficiency/Range (56% for general cars, #1 for EVs)
   
2. **Secondary Evaluation Criteria** (Used to compare within filtered set):
   - Safety (55% importance)
   - Brand Reputation & Trust (34-47% importance)
   - Quality/Reliability/Durability
   - Comfort & Features
   - Total Cost of Ownership (maintenance, fuel savings)
   
3. **EV-Specific Factors**:
   - Electric Range/Battery (Top concern globally)
   - Charging Infrastructure Access (49% in US, varies by region)
   - Price vs. Gas Vehicles (High purchase cost is #1 barrier)
   - Environmental Benefits (61% for EV buyers)
   - CAFV Eligibility & Incentives (40% don't understand them)
   - Hybrid as "Bridge" Option (26% prefer gradual transition)

4. **Emotional/Psychological Factors**:
   - Brand Loyalty & Image
   - Performance/Power (for enthusiasts)
   - Design/Aesthetics (32% importance)
   - Status/Reputation (especially for EVs)
   - Technology/Innovation Interest

DECISION PROCESS MODEL:
Step 1: Problem Recognition (What do I need? → Use Case/Mission)
Step 2: Budget Setting (Hard constraint)
Step 3: Body Style Selection (Non-compensatory for most)
Step 4: Search & Filter (Range, Type, Brand preferences)
Step 5: Alternative Evaluation (Compare top matches on multiple criteria)
Step 6: Purchase Decision (Final choice based on composite scoring)
"""

import pandas as pd
import streamlit as st


def create_improved_ev_advisor(df_filtered):
    """
    Create a research-based EV advisor that mirrors actual consumer decision-making.
    
    The advisor uses a hierarchical approach:
    1. Quick profiling for non-negotiables (mission, budget, range needs)
    2. Optional refinements (brand, type, CAFV, year)
    3. Multi-criteria scoring based on consumer research priorities
    4. Diverse recommendations showing different value propositions
    """
    
    st.markdown("---")
    st.subheader("💡 Smart EV Match Finder")
    st.caption("Find your perfect EV in 3 questions, or dive deeper with advanced filters")
    
    # Range requirements based on use case and range importance
    range_requirements = {
        "Daily commuting (< 50 mi/day)": {
            "Not critical (city driving)": 100,
            "Moderate (occasional trips)": 150,
            "Important (regular highway)": 200,
            "Essential (frequent road trips)": 250
        },
        "Regular road trips (> 200 mi)": {
            "Not critical (city driving)": 200,
            "Moderate (occasional trips)": 250,
            "Important (regular highway)": 300,
            "Essential (frequent road trips)": 350
        },
        "Family hauling & errands": {
            "Not critical (city driving)": 120,
            "Moderate (occasional trips)": 180,
            "Important (regular highway)": 240,
            "Essential (frequent road trips)": 280
        },
        "Weekend fun & performance": {
            "Not critical (city driving)": 150,
            "Moderate (occasional trips)": 200,
            "Important (regular highway)": 250,
            "Essential (frequent road trips)": 300
        },
        "General purpose / Not sure": {
            "Not critical (city driving)": 120,
            "Moderate (occasional trips)": 180,
            "Important (regular highway)": 220,
            "Essential (frequent road trips)": 260
        }
    }
    
    # Create tabs for different approaches
    tab_quick, tab_detailed, tab_search = st.tabs([
        "⚡ Quick Match (30 sec)", 
        "🎯 Detailed Profile (2 min)", 
        "🔍 Direct Search"
    ])
    
    # ============================================================================
    # TAB 1: QUICK MATCH - Minimal friction, maximum guidance
    # ============================================================================
    with tab_quick:
        st.markdown("### Answer 3 quick questions to get matched")
        
        with st.form("quick_match_form"):
            # Q1: Use Case (Problem Recognition)
            col1, col2 = st.columns([3, 1])
            with col1:
                use_case = st.selectbox(
                    "**1. What will you primarily use this EV for?**",
                    [
                        "Daily commuting (< 50 mi/day)",
                        "Regular road trips (> 200 mi)",
                        "Family hauling & errands",
                        "Weekend fun & performance",
                        "General purpose / Not sure"
                    ],
                    help="Your main use case determines range needs and vehicle type priorities"
                )
            
            # Q2: Budget (Hard Constraint - #1 factor for 55% of buyers)
            budget_ranges = {
                "Budget-conscious (< $40k)": (0, 40000),
                "Mid-range ($40k - $60k)": (40000, 60000),
                "Premium ($60k - $80k)": (60000, 80000),
                "Luxury (> $80k)": (80000, 999999),
                "No preference": (0, 999999)
            }
            
            budget_choice = st.selectbox(
                "**2. What's your budget range?**",
                list(budget_ranges.keys()),
                help="47% of EV buyers want vehicles under $40k - price is the #1 factor for most"
            )
            
            # Q3: Range Anxiety Level (Top EV concern globally)
            range_need = st.select_slider(
                "**3. How important is maximum electric range to you?**",
                options=[
                    "Not critical (city driving)",
                    "Moderate (occasional trips)",
                    "Important (regular highway)",
                    "Essential (frequent road trips)"
                ],
                value="Moderate (occasional trips)",
                help="Range anxiety is the #1 concern for 61% of potential EV buyers"
            )
            
            submit_quick = st.form_submit_button("🚀 Find My Best Matches", use_container_width=True)
        
        if submit_quick:
            # Apply non-compensatory filters (these are deal-breakers)
            candidates = df_filtered.copy()
            
            # Budget filter (hard constraint)
            min_price, max_price = budget_ranges[budget_choice]
            if 'Base MSRP' in candidates.columns:
                candidates = candidates[
                    (candidates['Base MSRP'].fillna(999999) >= min_price) &
                    (candidates['Base MSRP'].fillna(999999) <= max_price)
                ]
            
            # Range filter
            min_range = range_requirements[use_case][range_need]
            if 'Electric Range' in candidates.columns:
                candidates = candidates[candidates['Electric Range'].fillna(0) >= min_range]
            
            if candidates.empty:
                st.warning("⚠️ No vehicles match these criteria in the current dataset.")
                st.info(f"**Try adjusting:** Lower range requirement ({min_range} mi → {min_range-50} mi) or increase budget ({budget_choice})")
            else:
                # Multi-criteria scoring based on consumer research priorities
                display_recommendations(
                    candidates, 
                    use_case, 
                    budget_choice, 
                    range_need,
                    method="quick"
                )
    
    # ============================================================================
    # TAB 2: DETAILED PROFILE - For users who want control
    # ============================================================================
    with tab_detailed:
        st.markdown("### Complete profile for personalized recommendations")
        
        with st.form("detailed_profile_form"):
            # Primary factors (always shown)
            st.markdown("#### 🎯 Essential Factors")
            
            col1, col2 = st.columns(2)
            
            with col1:
                use_case_detailed = st.selectbox(
                    "Primary use case",
                    [
                        "Daily commuting (< 50 mi/day)",
                        "Regular road trips (> 200 mi)",
                        "Family hauling & errands",
                        "Weekend fun & performance",
                        "General purpose / Not sure"
                    ]
                )
                
                budget_detailed = st.selectbox(
                    "Budget range",
                    list(budget_ranges.keys())
                )
            
            with col2:
                range_need_detailed = st.select_slider(
                    "Range importance",
                    options=[
                        "Not critical (city driving)",
                        "Moderate (occasional trips)",
                        "Important (regular highway)",
                        "Essential (frequent road trips)"
                    ],
                    value="Moderate (occasional trips)"
                )
                
                # EV Type (33% prefer hybrid as bridge)
                ev_type_pref = st.selectbox(
                    "Powertrain preference",
                    ["Any (show me all)", "Battery Electric (BEV only)", "Plug-in Hybrid (PHEV only)"],
                    help="26% prefer hybrids as a bridge to full electric"
                )
            
            # Advanced factors (in expander)
            with st.expander("⚙️ Optional Refinements", expanded=False):
                st.markdown("#### Brand & Features")
                
                col3, col4 = st.columns(2)
                
                with col3:
                    # Brand preference (34-47% factor in brand)
                    available_makes = ["Any brand"] + sorted(df_filtered['Make'].dropna().unique().tolist()) if 'Make' in df_filtered.columns else ["Any brand"]
                    brand_pref = st.multiselect(
                        "Preferred brands (optional)",
                        available_makes[1:] if len(available_makes) > 1 else [],
                        help="34% consider brand reputation important, 47% have brand preferences"
                    )
                    
                    # Model year (freshness factor)
                    if 'Model Year' in df_filtered.columns:
                        year_min = int(df_filtered['Model Year'].min())
                        year_max = int(df_filtered['Model Year'].max())
                        year_pref = st.slider(
                            "Minimum model year",
                            min_value=year_min,
                            max_value=year_max,
                            value=max(year_min, year_max - 3),
                            help="Newer models often have better tech and safety features"
                        )
                
                with col4:
                    # CAFV eligibility (40% don't understand incentives)
                    cafv_pref = st.radio(
                        "Incentive eligibility",
                        ["Don't care", "Must be CAFV eligible", "Prefer CAFV eligible"],
                        help="40% of buyers don't understand EV incentives - this can save thousands"
                    )
                    
                    # Priority ranking
                    st.markdown("**What matters most to you?** (Rank top 3)")
                    priority_1 = st.selectbox("1st priority", 
                        ["Lowest price", "Longest range", "Brand reputation", "Latest technology", "Best value (range/price)"],
                        key="p1"
                    )
                    priority_2 = st.selectbox("2nd priority",
                        ["Longest range", "Lowest price", "Brand reputation", "Latest technology", "Best value (range/price)"],
                        key="p2"
                    )
                    priority_3 = st.selectbox("3rd priority",
                        ["Brand reputation", "Latest technology", "Best value (range/price)", "Lowest price", "Longest range"],
                        key="p3"
                    )
            
            submit_detailed = st.form_submit_button("🎯 Get Personalized Matches", use_container_width=True)
        
        if submit_detailed:
            # Apply all filters
            candidates_detailed = df_filtered.copy()
            
            # Budget
            min_price, max_price = budget_ranges[budget_detailed]
            if 'Base MSRP' in candidates_detailed.columns:
                candidates_detailed = candidates_detailed[
                    (candidates_detailed['Base MSRP'].fillna(999999) >= min_price) &
                    (candidates_detailed['Base MSRP'].fillna(999999) <= max_price)
                ]
            
            # Range
            min_range = range_requirements[use_case_detailed][range_need_detailed]
            if 'Electric Range' in candidates_detailed.columns:
                candidates_detailed = candidates_detailed[
                    candidates_detailed['Electric Range'].fillna(0) >= min_range
                ]
            
            # EV Type
            if ev_type_pref != "Any (show me all)" and 'Electric Vehicle Type' in candidates_detailed.columns:
                type_map = {
                    "Battery Electric (BEV only)": "Battery Electric Vehicle (BEV)",
                    "Plug-in Hybrid (PHEV only)": "Plug-in Hybrid Electric Vehicle (PHEV)"
                }
                candidates_detailed = candidates_detailed[
                    candidates_detailed['Electric Vehicle Type'] == type_map[ev_type_pref]
                ]
            
            # Brand
            if brand_pref and 'Make' in candidates_detailed.columns:
                candidates_detailed = candidates_detailed[
                    candidates_detailed['Make'].isin(brand_pref)
                ]
            
            # Year
            if 'year_pref' in locals() and 'Model Year' in candidates_detailed.columns:
                candidates_detailed = candidates_detailed[
                    candidates_detailed['Model Year'] >= year_pref
                ]
            
            # CAFV
            if cafv_pref != "Don't care" and 'Clean Alternative Fuel Vehicle (CAFV) Eligibility' in candidates_detailed.columns:
                cafv_col = 'Clean Alternative Fuel Vehicle (CAFV) Eligibility'
                if cafv_pref == "Must be CAFV eligible":
                    candidates_detailed = candidates_detailed[
                        candidates_detailed[cafv_col].astype(str).str.contains("eligible", case=False, na=False)
                    ]
                elif cafv_pref == "Prefer CAFV eligible":
                    # Don't filter, but boost score later
                    pass
            
            if candidates_detailed.empty:
                st.warning("⚠️ No vehicles match all criteria. Try relaxing some filters.")
            else:
                display_recommendations(
                    candidates_detailed,
                    use_case_detailed,
                    budget_detailed,
                    range_need_detailed,
                    method="detailed",
                    priorities=(priority_1, priority_2, priority_3) if 'priority_1' in locals() else None,
                    cafv_pref=cafv_pref
                )
    
    # ============================================================================
    # TAB 3: DIRECT SEARCH - For informed buyers
    # ============================================================================
    with tab_search:
        st.markdown("### Search directly if you know what you want")
        
        col_search, col_range = st.columns([2, 1])
        
        with col_search:
            search_query = st.text_input(
                "Search by make, model, type, or keyword",
                placeholder="e.g., Tesla Model 3, long range SUV, CAFV eligible",
                help="92% of buyers research online - search freely"
            )
        
        with col_range:
            if 'Electric Range' in df_filtered.columns:
                range_series = df_filtered['Electric Range'].dropna()
                if not range_series.empty:
                    search_min_range = st.slider(
                        "Min range (miles)",
                        min_value=int(range_series.min()),
                        max_value=int(range_series.max()),
                        value=int(range_series.quantile(0.3)),
                        step=10
                    )
                else:
                    search_min_range = 0
            else:
                search_min_range = 0
        
        if search_query or search_min_range > 0:
            search_results = df_filtered.copy()
            
            # Text search
            if search_query:
                query_lower = search_query.strip().lower()
                mask = False
                for col in ["Make", "Model", "Electric Vehicle Type", "Clean Alternative Fuel Vehicle (CAFV) Eligibility"]:
                    if col in search_results.columns:
                        col_mask = search_results[col].astype(str).str.lower().str.contains(query_lower, na=False)
                        mask = col_mask if mask is False else (mask | col_mask)
                if mask is not False:
                    search_results = search_results[mask]
            
            # Range filter
            if 'Electric Range' in search_results.columns and search_min_range > 0:
                search_results = search_results[
                    search_results['Electric Range'].fillna(0) >= search_min_range
                ]
            
            if search_results.empty:
                st.info("No matches found. Try broadening your search.")
            else:
                st.success(f"Found {len(search_results)} vehicles matching your search")
                
                # Show top result
                top_result = search_results.sort_values(
                    by=['Electric Range', 'Base MSRP'] if 'Base MSRP' in search_results.columns else ['Electric Range'],
                    ascending=[False, True] if 'Base MSRP' in search_results.columns else [False]
                ).iloc[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Top Match",
                        f"{top_result.get('Make', 'N/A')} {top_result.get('Model', '')}",
                        delta=f"{int(top_result['Electric Range'])} mi" if 'Electric Range' in top_result and not pd.isna(top_result['Electric Range']) else None
                    )
                with col2:
                    if 'Base MSRP' in top_result and not pd.isna(top_result['Base MSRP']):
                        st.metric("Price", f"${int(top_result['Base MSRP']):,}")
                    else:
                        st.metric("Type", top_result.get('Electric Vehicle Type', 'N/A'))
                with col3:
                    st.metric(
                        "Year",
                        int(top_result['Model Year']) if 'Model Year' in top_result and not pd.isna(top_result['Model Year']) else 'N/A'
                    )
                
                # Show results table
                display_cols = [c for c in ['Make', 'Model', 'Model Year', 'Electric Range', 'Base MSRP', 'Electric Vehicle Type', 'Clean Alternative Fuel Vehicle (CAFV) Eligibility'] if c in search_results.columns]
                st.dataframe(
                    search_results[display_cols].head(15),
                    use_container_width=True,
                    hide_index=True
                )


def display_recommendations(df, use_case, budget, range_need, method="quick", priorities=None, cafv_pref=None):
    """
    Display personalized recommendations using research-based scoring.
    
    Scoring weights based on consumer research:
    - Price: 55% cite as #1 factor
    - Range: #1 for EV buyers (61% concerned about range)
    - Brand/Quality: 34-47% importance
    - Newness/Tech: Varies by demographic
    - Value (Range/Price): 46% cite cost savings
    """
    
    if df.empty:
        return
    
    # Normalize scores (0-1 scale)
    score_df = df.copy()
    
    for col in ['Electric Range', 'Base MSRP', 'Model Year']:
        if col in score_df.columns:
            col_series = score_df[col].dropna()
            if not col_series.empty and col_series.min() != col_series.max():
                score_df[f'{col}_norm'] = (score_df[col] - col_series.min()) / (col_series.max() - col_series.min())
            else:
                score_df[f'{col}_norm'] = 0.5
        else:
            score_df[f'{col}_norm'] = 0.5
    
    # Calculate component scores
    score_df['range_score'] = score_df.get('Electric Range_norm', 0.5)
    score_df['price_score'] = 1 - score_df.get('Base MSRP_norm', 0.5)  # Lower price = higher score
    score_df['newness_score'] = score_df.get('Model Year_norm', 0.5)
    
    # Value score (range per dollar)
    if 'Electric Range' in score_df.columns and 'Base MSRP' in score_df.columns:
        score_df['value_raw'] = score_df['Electric Range'] / (score_df['Base MSRP'] + 1)
        if score_df['value_raw'].max() > score_df['value_raw'].min():
            score_df['value_score'] = (score_df['value_raw'] - score_df['value_raw'].min()) / (score_df['value_raw'].max() - score_df['value_raw'].min())
        else:
            score_df['value_score'] = 0.5
    else:
        score_df['value_score'] = 0.5
    
    # CAFV bonus (if preferred)
    if cafv_pref == "Prefer CAFV eligible" and 'Clean Alternative Fuel Vehicle (CAFV) Eligibility' in score_df.columns:
        score_df['cafv_bonus'] = score_df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].astype(str).str.contains("eligible", case=False, na=False).astype(float) * 0.1
    else:
        score_df['cafv_bonus'] = 0
    
    # Apply weights based on use case and priorities
    if method == "quick":
        # Research-based default weights
        use_case_weights = {
            "Daily commuting (< 50 mi/day)": {'price': 0.45, 'range': 0.20, 'value': 0.25, 'newness': 0.10},
            "Regular road trips (> 200 mi)": {'price': 0.25, 'range': 0.50, 'value': 0.15, 'newness': 0.10},
            "Family hauling & errands": {'price': 0.35, 'range': 0.30, 'value': 0.25, 'newness': 0.10},
            "Weekend fun & performance": {'price': 0.30, 'range': 0.30, 'value': 0.15, 'newness': 0.25},
            "General purpose / Not sure": {'price': 0.35, 'range': 0.30, 'value': 0.25, 'newness': 0.10}
        }
        weights = use_case_weights[use_case]
    else:
        # Custom weights based on stated priorities
        if priorities:
            p1, p2, p3 = priorities
            weight_map = {
                "Lowest price": 'price',
                "Longest range": 'range',
                "Brand reputation": 'newness',  # Proxy: newer models from better brands
                "Latest technology": 'newness',
                "Best value (range/price)": 'value'
            }
            
            # Priority 1 gets 50%, Priority 2 gets 30%, Priority 3 gets 20%
            weights = {'price': 0, 'range': 0, 'value': 0, 'newness': 0}
            weights[weight_map.get(p1, 'value')] += 0.50
            weights[weight_map.get(p2, 'price')] += 0.30
            weights[weight_map.get(p3, 'range')] += 0.20
        else:
            weights = {'price': 0.35, 'range': 0.30, 'value': 0.25, 'newness': 0.10}
    
    # Calculate composite score
    score_df['composite_score'] = (
        weights['price'] * score_df['price_score'] +
        weights['range'] * score_df['range_score'] +
        weights['value'] * score_df['value_score'] +
        weights['newness'] * score_df['newness_score'] +
        score_df['cafv_bonus']
    )
    
    # Sort by composite score
    ranked = score_df.sort_values('composite_score', ascending=False)
    
    # Show top recommendation
    st.markdown("---")
    st.markdown("### 🎯 Your Best Match")
    
    top_vehicle = ranked.iloc[0]
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown(f"""
        <div style="
            border: 2px solid #58a6ff;
            border-radius: 12px;
            padding: 1.5rem;
            background: linear-gradient(135deg, rgba(88,166,255,0.1), rgba(163,113,247,0.1));
        ">
            <h3 style="margin: 0; color: #f0f6fc;">{top_vehicle.get('Make', 'Unknown')} {top_vehicle.get('Model', '')} </h3>
            <p style="color: #8b949e; margin: 0.5rem 0;">
                {top_vehicle.get('Electric Vehicle Type', 'EV')} • {int(top_vehicle.get('Model Year', 0)) if pd.notna(top_vehicle.get('Model Year')) else 'N/A'}
            </p>
            <div style="display: flex; gap: 2rem; margin-top: 1rem; flex-wrap: wrap;">
                <div>
                    <p style="margin: 0; color: #8b949e; font-size: 0.9rem;">Range</p>
                    <strong style="font-size: 1.5rem; color: #58a6ff;">{int(top_vehicle['Electric Range']) if pd.notna(top_vehicle.get('Electric Range')) else 'N/A'}</strong>
                    <span style="color: #8b949e;"> mi</span>
                </div>
                <div>
                    <p style="margin: 0; color: #8b949e; font-size: 0.9rem;">Price</p>
                    <strong style="font-size: 1.5rem; color: #58a6ff;">${int(top_vehicle['Base MSRP']):,}</strong> if pd.notna(top_vehicle.get('Base MSRP')) else 'N/A'
                </div>
                <div>
                    <p style="margin: 0; color: #8b949e; font-size: 0.9rem;">Match Score</p>
                    <strong style="font-size: 1.5rem; color: #a371f7;">{top_vehicle['composite_score']:.0%}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**Why this match?**")
        
        # Explain the recommendation
        reasons = []
        if weights['price'] > 0.35:
            reasons.append(f"✓ Great value at ${int(top_vehicle.get('Base MSRP', 0)):,}")
        if weights['range'] > 0.35:
            reasons.append(f"✓ Excellent range: {int(top_vehicle.get('Electric Range', 0))} mi")
        if weights['value'] > 0.20:
            value_ratio = top_vehicle.get('Electric Range', 0) / (top_vehicle.get('Base MSRP', 1) / 1000)
            reasons.append(f"✓ Best value: {value_ratio:.1f} mi per $1k")
        if weights['newness'] > 0.20:
            reasons.append(f"✓ Latest tech ({int(top_vehicle.get('Model Year', 0))} model)")
        
        if 'Clean Alternative Fuel Vehicle (CAFV) Eligibility' in top_vehicle:
            cafv_status = top_vehicle['Clean Alternative Fuel Vehicle (CAFV) Eligibility']
            if pd.notna(cafv_status) and 'eligible' in str(cafv_status).lower():
                reasons.append("✓ Eligible for tax incentives")
        
        for reason in reasons:
            st.markdown(reason)
    
    # Show alternative options with diversity
    st.markdown("---")
    st.markdown("### 🔄 Alternative Options (Different Strengths)")
    
    alternatives = get_diverse_alternatives(ranked, top_vehicle)
    
    cols = st.columns(max(1, min(3, len(alternatives))))
    
    for idx, (title, vehicle, highlight) in enumerate(alternatives):
        with cols[idx]:
            range_val = int(vehicle['Electric Range']) if pd.notna(vehicle.get('Electric Range')) else 'N/A'
            price_val = f"${int(vehicle['Base MSRP']):,}" if pd.notna(vehicle.get('Base MSRP')) else 'N/A'
            year_val = int(vehicle['Model Year']) if pd.notna(vehicle.get('Model Year')) else 'N/A'
            
            st.markdown(f"""
            <div style="
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 1rem;
                background: rgba(33,38,45,0.5);
                height: 100%;
            ">
                <p style="color: #58a6ff; font-weight: 600; margin: 0 0 0.5rem 0; font-size: 0.85rem;">
                    {title}
                </p>
                <h4 style="margin: 0; color: #f0f6fc; font-size: 1.1rem;">
                    {vehicle.get('Make', 'Unknown')} {vehicle.get('Model', '')}
                </h4>
                <p style="color: #8b949e; font-size: 0.85rem; margin: 0.3rem 0;">
                    {year_val} • {vehicle.get('Electric Vehicle Type', 'EV')}
                </p>
                <div style="margin-top: 0.8rem;">
                    <span style="color: #8b949e; font-size: 0.8rem;">Range:</span>
                    <strong style="color: #f0f6fc;"> {range_val} mi</strong><br>
                    <span style="color: #8b949e; font-size: 0.8rem;">Price:</span>
                    <strong style="color: #f0f6fc;"> {price_val}</strong>
                </div>
                <p style="margin-top: 0.8rem; color: #a371f7; font-size: 0.85rem; font-weight: 500;">
                    {highlight}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    # Show comparison table
    st.markdown("---")
    st.markdown("### 📊 Compare Top 10 Matches")
    
    comparison_cols = [c for c in ['Make', 'Model', 'Model Year', 'Electric Range', 'Base MSRP', 'Electric Vehicle Type', 'Clean Alternative Fuel Vehicle (CAFV) Eligibility', 'composite_score'] if c in ranked.columns]
    
    # Rename composite_score for display
    display_df = ranked[comparison_cols].head(10).copy()
    if 'composite_score' in display_df.columns:
        display_df['Match Score'] = (display_df['composite_score'] * 100).round(0).astype(int).astype(str) + '%'
        display_df = display_df.drop('composite_score', axis=1)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Educational note
    st.info("""
    **💡 Pro tip:** According to consumer research, the top factors in EV purchases are:
    1. **Price** (55% say it's most important)
    2. **Range** (#1 concern for EV buyers - 61% worried about range anxiety)
    3. **Charging access** (49% in US concerned about infrastructure)
    4. **Brand trust** (34% factor in brand reputation)
    5. **Incentives** (but 40% don't understand them - check [fueleconomy.gov](https://fueleconomy.gov))
    """)


def get_diverse_alternatives(ranked_df, top_vehicle):
    """
    Get 2-3 alternative vehicles with different value propositions and brands.
    Ensures brand diversity and highlights different strengths.
    """
    alternatives = []
    used_makes = {top_vehicle.get('Make')}
    
    # Strategy 1: Best price from different brand
    price_candidates = ranked_df[~ranked_df['Make'].isin(used_makes)]
    if not price_candidates.empty and 'Base MSRP' in price_candidates.columns:
        best_price = price_candidates.nsmallest(1, 'Base MSRP').iloc[0]
        price_val = int(best_price['Base MSRP']) if pd.notna(best_price.get('Base MSRP')) else 0
        alternatives.append((
            "💰 Most Affordable",
            best_price,
            f"Best price alternative: ${price_val:,}"
        ))
        used_makes.add(best_price.get('Make'))
    
    # Strategy 2: Best range from different brand
    range_candidates = ranked_df[~ranked_df['Make'].isin(used_makes)]
    if not range_candidates.empty and 'Electric Range' in range_candidates.columns:
        best_range = range_candidates.nsmallest(1, 'Electric Range', keep='last').iloc[-1]
        range_val = int(best_range['Electric Range']) if pd.notna(best_range.get('Electric Range')) else 0
        alternatives.append((
            "⚡ Longest Range",
            best_range,
            f"Maximum range: {range_val} miles"
        ))
        used_makes.add(best_range.get('Make'))
    
    # Strategy 3: Best value (range/price) from different brand
    value_candidates = ranked_df[~ranked_df['Make'].isin(used_makes)]
    if not value_candidates.empty and 'value_score' in value_candidates.columns:
        best_value = value_candidates.nlargest(1, 'value_score').iloc[0]
        if 'Electric Range' in best_value and 'Base MSRP' in best_value:
            range_val = best_value.get('Electric Range', 0)
            price_val = best_value.get('Base MSRP', 1)
            value_ratio = range_val / (price_val / 1000) if price_val > 0 else 0
            alternatives.append((
                "⭐ Best Value",
                best_value,
                f"{value_ratio:.1f} mi per $1k spent"
            ))
    
    return alternatives[:3]
