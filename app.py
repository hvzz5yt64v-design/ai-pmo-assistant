import streamlit as st
import pandas as pd
import json
from openai import OpenAI

st.title("AI PMOアシスタント")

meeting_minutes = st.text_area(
    "会議の議事録を入力してください",
    height=250
)

if st.button("議事録を分析する"):
    if not meeting_minutes.strip():
        st.warning("議事録を入力してください。")
    else:
        try:
            client = OpenAI()

            prompt = f"""
あなたはPMOアシスタントです。
以下の議事録を分析してください。

議事録：
{meeting_minutes}

担当者や期限が不明な場合は「未確認」としてください。
推測で情報を補わないでください。

JSON形式で出力してください。
{{
  "summary": "会議の要約",
  "issues": [
    {{
      "issue": "課題",
      "todo": "対応事項",
      "owner": "担当者",
      "due_date": "期限",
      "status": "ステータス",
      "risk": "リスク",
      "impact": "影響",
      "response": "対応案"
    }}
  ]
}}
"""

            with st.spinner("AIが分析しています..."):
                response = client.responses.create(
                    model="gpt-4.1-mini",
                    input=prompt,
                    text={"format": {"type": "json_object"}}
                )

            result = json.loads(response.output_text)

            st.subheader("会議の要約")
            st.write(result["summary"])

            df = pd.DataFrame(result["issues"])
            df = df.rename(columns={
                "issue": "課題",
                "todo": "ToDo",
                "owner": "担当者",
                "due_date": "期限",
                "status": "ステータス",
                "risk": "リスク",
                "impact": "影響",
                "response": "対応案"
            })

            df.insert(
                0, "課題ID",
                [f"ISSUE-{i+1:03d}" for i in range(len(df))]
            )

            st.subheader("課題・ToDo一覧")
            st.dataframe(df, use_container_width=True)

            st.subheader("簡易リスク分析")
            for _, row in df.iterrows():
                st.markdown(f"**{row['課題ID']}：{row['課題']}**")
                st.write("リスク：" + str(row["リスク"]))
                st.write("影響：" + str(row["影響"]))
                st.write("対応案：" + str(row["対応案"]))

            csv_columns = [
                "課題ID", "課題", "ToDo",
                "担当者", "期限", "ステータス"
            ]

            csv_data = df[csv_columns].to_csv(
                index=False,
                encoding="utf-8-sig"
            )

            st.download_button(
                "CSVをダウンロード",
                data=csv_data,
                file_name="AI_PMO_課題管理一覧.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"分析エラー：{e}")
