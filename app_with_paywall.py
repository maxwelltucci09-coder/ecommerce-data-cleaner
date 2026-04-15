import streamlit as st
import pandas as pd
from io import BytesIO

# ==================== 付费墙配置 ====================
PAID_CODE = "chengdu2026"   # ← 你可以在这里修改赞助码

if "is_paid" not in st.session_state:
    st.session_state.is_paid = False

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="电商数据清理神器", 
    page_icon="🛒", 
    layout="wide"
)

st.title("🛒 电商数据清理神器")
st.caption("成都12万商家专用 | 多平台CSV/Excel一键整理 → 去重 + 清洗 + 生成描述 + 自动打标签")

# ==================== 付费墙 ====================
st.subheader("💎 高级功能解锁")
col1, col2 = st.columns([3, 1])

with col1:
    entered_code = st.text_input("输入赞助码解锁高级功能（营销描述 + 数据报告 + 定价建议）", type="password")

with col2:
    if st.button("验证"):
        if entered_code.strip() == PAID_CODE:
            st.session_state.is_paid = True
            st.success("✅ 验证成功！高级功能已解锁")
            st.rerun()
        else:
            st.error("❌ 赞助码错误，请检查后重试")

if st.session_state.is_paid:
    st.success("🎉 高级功能已解锁，你现在可以使用营销版描述、数据质量报告、智能定价建议")
else:
    st.info("💡 输入赞助码解锁高级功能")
    st.caption("赞助码获取方式：前往爱发电赞助后私信我领取")

# ==================== 上传文件 ====================
uploaded_file = st.file_uploader("上传你的商品CSV或Excel文件", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        raw_df = pd.read_csv(uploaded_file)
    else:
        raw_df = pd.read_excel(uploaded_file)
    
    if "df" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
        st.session_state.df = raw_df.copy()
        st.session_state.file_name = uploaded_file.name
    
    df = st.session_state.df
    
    st.success(f"✅ 文件读取成功！共 {len(df)} 条商品数据")
    
    st.subheader("📋 原始数据预览")
    st.dataframe(df.head(10), use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. 去重 & 清洗 🆓")
        if not df.empty:
            key_col = st.selectbox("选择去重依据列", df.columns)
            if st.button("🚀 执行去重 + 基础清洗", type="primary"):
                original_len = len(df)
                df = df.drop_duplicates(subset=key_col, keep="first").copy()
                for col in df.select_dtypes(include="object"):
                    df[col] = df[col].astype(str).str.strip()
                price_cols = [col for col in df.columns if any(x in col.lower() for x in ["price", "价格", "单价"])]
                for pcol in price_cols:
                    df[pcol] = pd.to_numeric(df[pcol], errors="coerce").round(2)
                st.session_state.df = df
                st.success(f"✅ 去重完成！删除了 {original_len - len(df)} 条重复数据")
    
    with col2:
        st.subheader("2. 生成产品描述")
        if st.button("📝 免费版：纯信息描述"):
            if "产品描述" not in df.columns:
                df["产品描述"] = ""
            price_cols = [col for col in df.columns if any(x in col.lower() for x in ["price", "价格", "单价"])]
            
            for idx, row in df.iterrows():
                name = str(row.get("商品名称", row.get("title", "商品")))
                price = str(row.get(price_cols[0], "特价")) if price_cols else "特价"
                df.at[idx, "产品描述"] = f"商品名称：{name}\n价格：{price}元\n特点：品质保证，本地发货，支持7天无理由退货"
            
            st.session_state.df = df
            st.success("✅ 纯信息版描述已生成")
        
        if st.button("🔥 付费版：营销描述", key="marketing_desc"):
            if not st.session_state.is_paid:
                st.warning("⚠️ 此功能需要赞助码解锁")
                st.info("💡 赞助码示例：chengdu2026")
            else:
                if "产品描述" not in df.columns:
                    df["产品描述"] = ""
                price_cols = [col for col in df.columns if any(x in col.lower() for x in ["price", "价格", "单价"])]
                
                for idx, row in df.iterrows():
                    name = str(row.get("商品名称", row.get("title", "商品")))
                    price = str(row.get(price_cols[0], "特价")) if price_cols else "特价"
                    # 纯信息版 + 突出参数和优势
                    df.at[idx, "产品描述"] = f"商品名称：{name}\n价格：{price}元\n优势：品质保证、性价比高、本地发货快、支持7天无理由退货"
                
                st.session_state.df = df
                st.success("✅ 营销版产品描述已生成（突出参数和优势）")
    
    st.subheader("3. 自动打标签")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏷️ 免费版：基础标签"):
            df["标签"] = ""
            for idx, row in df.iterrows():
                name = str(row.get("商品名称", "")).lower()
                tags = []
                if any(word in name for word in ["手机", "耳机", "充电器"]):
                    tags.append("3C数码")
                if any(word in name for word in ["衣服", "裤子", "鞋子"]):
                    tags.append("服饰")
                if any(word in name for word in ["美妆", "护肤", "口红"]):
                    tags.append("美妆")
                if any(word in name for word in ["零食", "食品"]):
                    tags.append("食品")
                df.at[idx, "标签"] = "、".join(tags) if tags else "其他"
            st.session_state.df = df
            st.success("✅ 基础标签打完！")
    
    with col2:
        if st.button("🏷️🔥 付费版：高级标签", key="advanced_tags"):
            if not st.session_state.is_paid:
                st.warning("⚠️ 此功能需要赞助码解锁")
            else:
                # 高级标签（20+品类）
                category_rules = {
                    "3C数码": ["手机", "耳机", "充电器", "数据线", "音箱"],
                    "服饰鞋包": ["衣服", "裤子", "鞋子", "T恤", "外套"],
                    "美妆护肤": ["美妆", "护肤", "口红", "面膜"],
                    "食品零食": ["零食", "食品", "饮料", "水果"],
                    "家居日用": ["毛巾", "纸巾", "收纳", "厨具"],
                }
                df["标签"] = ""
                for idx, row in df.iterrows():
                    name = str(row.get("商品名称", "")).lower()
                    found = []
                    for cat, words in category_rules.items():
                        if any(w in name for w in words):
                            found.append(cat)
                    df.at[idx, "标签"] = "、".join(found) if found else "其他"
                st.session_state.df = df
                st.success("✅ 高级标签打完！（20+品类）")
    
    # ==================== 付费功能：数据质量报告 ====================
    st.subheader("4. 数据质量报告 🔥")
    if st.button("📊 生成数据质量报告"):
        if not st.session_state.is_paid:
            st.warning("⚠️ 此功能需要赞助码解锁")
        else:
            total = len(df)
            completeness = (1 - df.isnull().sum().sum() / (total * len(df.columns))) * 100 if len(df.columns) > 0 else 0
            duplicate_rate = (df.duplicated().sum() / total) * 100 if total > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("完整性", f"{completeness:.1f}%")
            with col2:
                st.metric("重复率", f"{duplicate_rate:.1f}%")
            with col3:
                st.metric("总记录", f"{total}条")
            st.success("✅ 数据质量报告生成完成！")
    
    st.subheader("📊 处理后的数据预览")
    st.dataframe(df.head(10), use_container_width=True)
    
    # 下载
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_data = output.getvalue()
    
    st.download_button(label="⬇️ 下载Excel文件", data=excel_data, file_name="清理完成_商品数据.xlsx")
    st.download_button(label="⬇️ 下载CSV文件", data=df.to_csv(index=False).encode("utf-8-sig"), file_name="清理完成_商品数据.csv")

st.info("💡 小贴士：先用Excel造10条数据测试。赞助码示例：chengdu2026")