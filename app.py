import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="电商数据清理神器", page_icon="🛒", layout="wide")
st.title("🛒 电商数据清理神器")
st.caption("成都12万商家专用 | 多平台CSV/Excel一键整理 → 去重 + 清洗 + 生成描述 + 自动打标签")

# 上传文件
uploaded_file = st.file_uploader("上传你的商品CSV或Excel文件", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # 自动检测格式并读取
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # 初始化session_state
    if 'processed_df' not in st.session_state:
        st.session_state.processed_df = df.copy()
    
    st.success(f"✅ 文件读取成功！共 {len(df)} 条商品数据")
    
    # 显示原始数据预览
    with st.expander("📋 查看原始数据"):
        st.dataframe(df.head(10), use_container_width=True)
    
    # 提前识别价格列（避免变量作用域问题）
    price_cols = [col for col in df.columns if any(x in col.lower() for x in ["price", "价格", "单价"])]
    
    # ====================== 功能区 ======================
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("1️⃣ 去重 & 清洗")
        key_col = st.selectbox("选择去重依据列", df.columns, key="dedup_col")
        
        if st.button("🚀 执行去重清洗", type="primary"):
            original_len = len(st.session_state.processed_df)
            st.session_state.processed_df = st.session_state.processed_df.drop_duplicates(subset=key_col, keep="first")
            
            # 清理空格
            for col in st.session_state.processed_df.select_dtypes(include="object"):
                st.session_state.processed_df[col] = st.session_state.processed_df[col].astype(str).str.strip()
            
            # 价格标准化
            for pcol in price_cols:
                if pcol in st.session_state.processed_df.columns:
                    st.session_state.processed_df[pcol] = pd.to_numeric(st.session_state.processed_df[pcol], errors="coerce").round(2)
            
            st.success(f"✅ 去重完成！删除 {original_len - len(st.session_state.processed_df)} 条重复，已清理空格+标准化价格")
    
    with col2:
        st.subheader("2️⃣ 生成描述")
        if st.button("✍️ 一键生成描述"):
            desc_col = "产品描述"
            if desc_col not in st.session_state.processed_df.columns:
                st.session_state.processed_df[desc_col] = ""
            
            for idx, row in st.session_state.processed_df.iterrows():
                name = str(row.get("商品名称", row.get("title", "商品")))
                price = str(row.get(price_cols[0], "特价")) if price_cols else "特价"
                st.session_state.processed_df.at[idx, desc_col] = f"【热销爆款】{name} 成都发货 限时{price}元！"
            
            st.success("✅ 描述生成完成！")
    
    with col3:
        st.subheader("3️⃣ 自动打标签")
        if st.button("🏷️ 一键打标签"):
            tags_list = []
            for idx, row in st.session_state.processed_df.iterrows():
                name = str(row.get("商品名称", "")).lower()
                tags = []
                if any(w in name for w in ["手机", "耳机", "充电器"]): tags.append("3C数码")
                if any(w in name for w in ["衣服", "裤子", "鞋子"]): tags.append("服饰")
                if any(w in name for w in ["美妆", "护肤"]): tags.append("美妆")
                if any(w in name for w in ["零食", "食品"]): tags.append("食品")
                tags_list.append("、".join(tags) if tags else "其他")
            st.session_state.processed_df["标签"] = tags_list
            st.success("✅ 标签完成！")
    
    # ====================== 结果 ======================
    st.divider()
    st.subheader("📊 处理结果")
    st.dataframe(st.session_state.processed_df.head(20), use_container_width=True)
    
    # 下载
    col_down1, col_down2 = st.columns(2)
    with col_down1:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            st.session_state.processed_df.to_excel(writer, index=False)
        st.download_button("⬇️ 下载Excel", output.getvalue(), "清理完成.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    with col_down2:
        st.download_button("⬇️ 下载CSV", st.session_state.processed_df.to_csv(index=False).encode("utf-8-sig"), "清理完成.csv", "text/csv")

st.info("💡 小贴士：先用Excel造10条测试数据（商品名称、价格、SKU等列）")