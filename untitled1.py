import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 1. 設定頁面配置
st.set_page_config(page_title="Probe Mechanics Demo", page_icon="🔬", layout="wide")

# 2. 標題與說明
st.title("🔬 Probe Card Mechanics: Why Isolated Pins Fail?")
st.markdown("""
### 工程原理展示：孤立針 (Isolated Pin) vs. 群組針 (Grouped Pins)
此模擬器展示探針卡在 **晶圓邊緣 (Wafer Edge)** 的受力行為差異，解釋為何外圍孤立針容易發生變形。
""")

# 3. Sidebar 設定 (參數控制)
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
    - 🟥 **Red**: 危險/滑移 (Risk/Slip)
    - 🟦 **Blue**: 安全/支撐 (Safe/Support)
    - ⬛ **Black**: 下壓力 (Overdrive)
    """)

# 4. 核心繪圖邏輯
def draw_simulation(scenario_type, show_vectors):
    # 建立畫布
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # --- 定義幾何參數 ---
    # 晶圓 (Wafer) 輪廓：平坦區 + 邊緣斜坡 (Bevel)
    x_wafer = np.linspace(0, 10, 200)
    slope_start = 7.5
    # 建立斜坡邏輯: 超過 slope_start 後開始往下掉
    y_wafer = np.array([2.0 if x < slope_start else 2.0 - (x-slope_start)*1.5 for x in x_wafer])
    
    # 繪製 Wafer
    ax.fill_between(x_wafer, 0, y_wafer, color='#E0E0E0', label='Wafer')
    ax.text(3.5, 1.0, "Silicon Wafer (Substrate)", color='gray', fontsize=12, ha='center')
    ax.text(8.5, 0.5, "Edge Bevel\n(斜坡)", color='gray', fontsize=10, ha='center', rotation=-45)

    # 設定探針卡高度與狀態
    head_color = '#444444'
    pin_color = '#222222'
    
    # 判斷模式
    is_grouped = "Grouped" in scenario_type
    
    # 設定 Probe Head 高度
    # Grouped: 有人頂住 -> 高度較高 (y=7)
    # Isolated: 沒人頂住 -> Overdrive 下壓 -> 高度較低 (y=6)
    head_y = 7.0 if is_grouped else 6.0
    
    # 繪製 Probe Head (卡座)
    rect_head = patches.Rectangle((1, head_y), 8.5, 1.0, linewidth=0, facecolor=head_color, alpha=0.8)
    ax.add_patch(rect_head)
    ax.text(5.25, head_y + 0.4, "Probe Card Head (Ceramic)", color='white', ha='center', fontsize=10)

    # --- 繪製探針 (Needles) ---
    if is_grouped:
        # === 安全模式：有鄰居 ===
        # 繪製 Pads
        ax.add_patch(patches.Rectangle((2, 2.0), 1, 0.2, color='#FFD700')) # Pad 1
        ax.add_patch(patches.Rectangle((4.5, 2.0), 1, 0.2, color='#FFD700')) # Pad 2
        
        # Pin 1 (Support)
        ax.plot([2.5, 2.5], [2.2, head_y], color=pin_color, linewidth=3)
        # Pin 2 (Support)
        ax.plot([5.0, 5.0], [2.2, head_y], color=pin_color, linewidth=3)
        # Pin 3 (Edge Pin - Safe)
        # 雖然懸空，但因為 Head 停在 y=7，針長固定，所以針尖停在 y=2.2 (假設針長4.8)
        ax.plot([8.0, 8.0], [head_y - 4.8, head_y], color=pin_color, linewidth=3, linestyle='--')
        
        # 狀態標示
        ax.text(5.0, 8.5, "SAFE: Supported by Neighbors", color='green', fontsize=14, ha='center', fontweight='bold')
        
        if show_vectors:
            # 藍色支撐力
            ax.arrow(2.5, 2.2, 0, 1.2, head_width=0.2, fc='blue', ec='blue')
            ax.arrow(5.0, 2.2, 0, 1.2, head_width=0.2, fc='blue', ec='blue')
            ax.text(3.75, 4.0, "Support Force\n(Z-Stop)", color='blue', ha='center', fontweight='bold')

    else:
        # === 危險模式：孤立針 ===
        # 沒 Pad 支撐，Head 已經壓到 y=6 (Overdrive)
        # 針原本要在 x=8.0，但遇到斜坡
        
        # 繪製變形的針 (使用折線模擬)
        # 起點 (Head): (8.0, 6.0)
        # 著地點 (Slope): 約在 x=8.5, y=0.5 (滑出去了)
        # 彎折點 (Buckling): x=7.8, y=3.5 (往外凸)
        
        x_bent = [8.0, 7.8, 8.5]
        y_bent = [6.0, 3.5, 0.5]
        
        ax.plot(x_bent, y_bent, color='red', linewidth=4)
        ax.scatter([8.5], [0.5], color='red', s=100, marker='X', zorder=5)
        
        # 狀態標示
        ax.text(5.0, 8.5, "FAIL: Sliding & Bending!", color='red', fontsize=14, ha='center', fontweight='bold')
        
        if show_vectors:
            # 黑色下壓力
            ax.arrow(8.0, 6.0, 0, -1.5, head_width=0.2, fc='black', ec='black')
            ax.text(7.5, 5.0, "Overdrive\n(No Stop)", color='black', ha='right')
            
            # 紅色側向力
            ax.arrow(8.5, 0.5, 0.8, -0.8, head_width=0.2, fc='red', ec='red')
            ax.text(9.0, 0.8, "Lateral Slip\n(Force)", color='red', ha='left', fontweight='bold')

    # 版面設定
    ax.set_xlim(0, 10)
    ax.set_ylim(-1, 9)
    ax.axis('off') # 隱藏座標軸
    
    return fig

# 5. 執行繪圖與佈局
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### 📝 Engineering Analysis")
    if "Grouped" in scenario:
        st.success("""
        **✅ Scenario A: 群組針 (安全)**
        
        * **機制**: 內側探針踩在 Pad 上，提供反作用力 (Z-Stop)。
        * **結果**: 即使外圍針懸空，探針卡已被頂住，不會過度下壓。
        * **結論**: 針體保持直立，無損傷。
        """)
    else:
        st.error("""
        **❌ Scenario B: 孤立針 (危險)**
        
        * **機制**: 無鄰居支撐，機台持續過度下壓 (Overdrive)。
        * **失效**: 針尖接觸斜坡時，產生巨大的 **側向分力 (Lateral Force)**。
        * **結果**: 針尖滑移 (Skid)，針身發生塑性變形 (Bent)。
        """)

with col2:
    fig = draw_simulation(scenario, show_force)
    st.pyplot(fig)

st.caption("Generated by Gemini for Irene's 8D Report Visualization.")
