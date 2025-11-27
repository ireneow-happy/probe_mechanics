
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 1. 設定頁面配置
st.set_page_config(page_title="Probe Mechanics Demo (Bump)", page_icon="🔬", layout="wide")

# 2. 標題與說明
st.title("🔬 Probe Card Mechanics: Why Isolated Pins Fail?")
st.markdown("""
### 工程原理展示：孤立針 (Isolated Pin) vs. 群組針 (Grouped Pins)
此模擬器展示探針卡在 **晶圓邊緣 (Wafer Edge)** 的受力行為差異。
特別針對 **Solder Bump (錫球)** 製程，解釋為何外圍孤立針容易在 Edge Bevel 處發生滑移與變形。
""")

# 3. Sidebar 設定
with st.sidebar:
    st.header("⚙️ Simulation Settings")
    scenario = st.radio(
        "選擇情境 (Scenario):",
        ("Scenario A: Grouped Pins (Safe)", "Scenario B: Isolated Pin (Risk)"),
        index=0
    )
    
    show_force = st.toggle("顯示受力箭頭 (Force Vectors)", value=True)
    
    st.info("""
    **圖例說明:**
    - 🟡 **Gold**: 錫球 (Solder Bump)
    - 🟥 **Red**: 危險/滑移 (Risk/Slip)
    - 🟦 **Blue**: 安全/支撐 (Safe/Support)
    - ⬛ **Black**: 下壓力 (Overdrive)
    """)

# 4. 核心繪圖邏輯
def draw_simulation(scenario_type, show_vectors):
    # 建立畫布
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # --- 定義幾何參數 ---
    # 晶圓 (Wafer) 輪廓
    x_wafer = np.linspace(0, 10, 200)
    slope_start = 7.5
    y_wafer = np.array([2.0 if x < slope_start else 2.0 - (x-slope_start)*1.5 for x in x_wafer])
    
    # 繪製 Wafer 基板
    ax.fill_between(x_wafer, 0, y_wafer, color='#E0E0E0', label='Wafer')
    ax.text(3.5, 1.0, "Silicon Wafer", color='gray', fontsize=12, ha='center')
    ax.text(8.5, 0.5, "Edge Bevel\n(斜坡)", color='gray', fontsize=10, ha='center', rotation=-45)

    # 設定探針卡高度
    head_color = '#444444'
    pin_color = '#222222'
    is_grouped = "Grouped" in scenario_type
    
    # Bump 參數
    bump_radius = 0.5
    bump_height = 2.0 # Wafer surface y
    
    # 設定 Probe Head 高度
    # Grouped: 針尖頂在 Bump 上 (y=2.5) -> Head 高度較高 (y=7.5)
    # Isolated: 針尖滑到斜坡 (y=0.5) -> Head 被 OD 壓低 (y=6.5)
    head_y = 7.5 if is_grouped else 6.5
    
    # 繪製 Probe Head
    rect_head = patches.Rectangle((1, head_y), 8.5, 1.0, linewidth=0, facecolor=head_color, alpha=0.8)
    ax.add_patch(rect_head)
    ax.text(5.25, head_y + 0.4, "Probe Card Head", color='white', ha='center', fontsize=10)

    # --- 繪製探針 (Needles) ---
    if is_grouped:
        # === 安全模式：有鄰居 (Bumps) ===
        # 繪製 Solder Bumps (半圓形)
        bump1 = patches.Wedge((2.5, bump_height), bump_radius, 0, 180, color='#FFD700')
        bump2 = patches.Wedge((5.0, bump_height), bump_radius, 0, 180, color='#FFD700')
        ax.add_patch(bump1)
        ax.add_patch(bump2)
        
        # 針尖接觸點 (Bump Top)
        contact_y = bump_height + bump_radius # 2.0 + 0.5 = 2.5
        
        # Pin 1 (Support)
        ax.plot([2.5, 2.5], [contact_y, head_y], color=pin_color, linewidth=3)
        # Pin 2 (Support)
        ax.plot([5.0, 5.0], [contact_y, head_y], color=pin_color, linewidth=3)
        
        # Pin 3 (Edge Pin) - 懸空
        # 針長 = 7.5 - 2.5 = 5.0
        # 針尖位置 = Head_y - 5.0
        tip_y_3 = head_y - 5.0
        ax.plot([8.0, 8.0], [tip_y_3, head_y], color=pin_color, linewidth=3, linestyle='--')
        
        # 狀態標示
        ax.text(5.0, 8.8, "SAFE: Supported by Bumps", color='green', fontsize=14, ha='center', fontweight='bold')
        
        if show_vectors:
            # 藍色支撐力 (從 Bump 往上)
            ax.arrow(2.5, contact_y, 0, 1.2, head_width=0.2, fc='blue', ec='blue')
            ax.arrow(5.0, contact_y, 0, 1.2, head_width=0.2, fc='blue', ec='blue')
            ax.text(3.75, 4.5, "Support Force\n(Z-Stop)", color='blue', ha='center', fontweight='bold')

    else:
        # === 危險模式：孤立針 (無 Bump 支撐) ===
        # 假設這是最外圈，沒有 Bump，或者針完全偏掉沒踩到 Bump
        
        # 繪製變形的針
        # 起點 (Head): (8.0, 6.5)
        # 著地點 (Slope): (8.5, 0.5)
        # 彎折點: (7.8, 3.5)
        
        x_bent = [8.0, 7.8, 8.5]
        y_bent = [head_y, 3.5, 0.5]
        
        ax.plot(x_bent, y_bent, color='red', linewidth=4)
        ax.scatter([8.5], [0.5], color='red', s=100, marker='X', zorder=5)
        
        # 狀態標示
        ax.text(5.0, 8.8, "FAIL: Sliding on Bevel", color='red', fontsize=14, ha='center', fontweight='bold')
        
        if show_vectors:
            # 黑色下壓力
            ax.arrow(8.0, head_y, 0, -1.5, head_width=0.2, fc='black', ec='black')
            ax.text(7.5, 5.5, "Overdrive\n(No Bump Stop)", color='black', ha='right')
            
            # 紅色側向力
            ax.arrow(8.5, 0.5, 0.8, -0.8, head_width=0.2, fc='red', ec='red')
            ax.text(9.0, 0.8, "Lateral Slip\n(Force)", color='red', ha='left', fontweight='bold')

    # 版面設定
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 9.5) # 增加高度空間
    ax.axis('off')
    
    return fig

# 5. 執行繪圖與佈局
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📝 Engineering Analysis")
    if "Grouped" in scenario:
        st.success("""
        **✅ Scenario A: 群組針 (安全)**
        
        * **機制**: 內側探針準確扎在 **Solder Bump** 上，提供反作用力 (Z-Stop)。
        * **結果**: 即使外圍針懸空，探針卡已被 Bumps 頂住，不會過度下壓。
        * **結論**: 針體保持直立，無損傷。
        """)
    else:
        st.error("""
        **❌ Scenario B: 孤立針 (危險)**
        
        * **機制**: 該針位為 **Isolated Pin**，周圍無 Bump 或鄰近針腳支撐。
        * **失效**: 誤觸 Wafer Edge Bevel，因無 Z-Stop，機台持續 Overdrive。
        * **結果**: 針尖沿斜坡滑移，導致針身變形 (Bent Needle)。
        """)

with col2:
    fig = draw_simulation(scenario, show_force)
    st.pyplot(fig)

st.caption("Generated by Gemini for Irene's 8D Report.")
