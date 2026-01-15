import streamlit as st
import sys
from pathlib import Path
import time

# 프로젝트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from chains.qa_chain import get_qa_chain
from vectorstore.retriever import get_retriever

# Streamlit 페이지 설정
st.set_page_config(
    page_title="보험 약관 Q&A 챗봇",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .source-box {
        background-color: #fff9e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
        margin-top: 1rem;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ff6b6b;
        margin-top: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 5px solid #ffc107;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
    st.session_state.conversation_history = []
    st.session_state.qdrant_ready = False
    st.session_state.init_attempted = False

# 헤더
st.markdown('<h1 class="main-header">🏠 보험 약관 Q&A 챗봇</h1>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #666; margin-bottom: 2rem;">
    <p>Solar 모델 기반의 지능형 보험 상담 시스템</p>
    <p>정확한 약관 조항을 근거로 답변해드립니다</p>
</div>
""", unsafe_allow_html=True)

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    st.markdown("---")
    
    st.subheader("📊 대화 통계")
    st.metric("질문 수", len(st.session_state.conversation_history))
    
    st.markdown("---")
    
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.conversation_history = []
        st.rerun()
    
    st.markdown("---")
    
    st.subheader("💡 사용 팁")
    st.info("""
    **질문 예시:**
    - "화재보험 보장 범위는?"
    - "장해지급률 3은 보험금을 받을 수 있나?"
    - "자해는 보상되나요?"
    """)
    
    st.markdown("---")
    
    st.subheader("🔗 보험 상품")
    insurance_types = [
        "상해보험",
        "손해보험",
        "질병보험",
        "책임보험",
        "화재보험"
    ]
    for ins in insurance_types:
        st.caption(f"✓ {ins}")

# 메인 콘텐츠
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.subheader("💬 질문 입력")
    
    # Qdrant 연결 상태 확인
    if not st.session_state.init_attempted:
        st.session_state.init_attempted = True
        with st.spinner("🔄 시스템 초기화 중..."):
            try:
                # Qdrant 연결 테스트
                retriever = get_retriever()
                st.session_state.qdrant_ready = True
                st.session_state.qa_chain = get_qa_chain()
            except ConnectionRefusedError as e:
                st.session_state.qdrant_ready = False
                st.markdown("""
<div class="error-box">
<h3>❌ Qdrant 서버 연결 실패</h3>
<p><b>오류:</b> Qdrant 서버에 연결할 수 없습니다.</p>
<p><b>해결 방법:</b></p>
<ol>
<li><b>Docker 시작:</b>
<pre>docker run -p 6333:6333 qdrant/qdrant</pre>
또는 Docker Desktop 애플리케이션을 실행하세요.</li>
<li>위 명령 후 이 페이지를 새로고침하세요 (F5)</li>
<li>계속해서 오류가 발생하면 터미널에서 다음을 확인하세요:
<pre>docker ps</pre></li>
</ol>
<p><b>상세 오류:</b> {}</p>
</div>
""".format(str(e)), unsafe_allow_html=True)
            except Exception as e:
                st.session_state.qdrant_ready = False
                st.markdown(f"""
<div class="error-box">
<h3>❌ 시스템 초기화 오류</h3>
<p><b>오류 메시지:</b> {str(e)}</p>
<p><b>해결 방법:</b></p>
<ol>
<li>Docker가 실행 중인지 확인하세요: <code>docker ps</code></li>
<li>Qdrant 서버가 실행 중인지 확인하세요: <code>docker run -p 6333:6333 qdrant/qdrant</code></li>
<li>.env 파일의 UPSTAGE_API_KEY가 설정되어 있는지 확인하세요</li>
<li>페이지를 새로고침하세요 (F5)</li>
</ol>
</div>
""", unsafe_allow_html=True)
    
    # Qdrant 준비됨 - 질문 입력 허용
    if st.session_state.qdrant_ready and st.session_state.qa_chain is not None:
        question = st.text_input(
            "보험에 대해 궁금한 점을 물어보세요:",
            placeholder="예: 화재보험 보장 범위는 무엇입니까?",
            label_visibility="collapsed"
        )
        
        # 질문 처리
        if question:
            with st.spinner("🔍 약관을 검색하고 답변을 생성 중입니다..."):
                try:
                    # 답변 생성
                    answer = st.session_state.qa_chain.invoke(question)
                    
                    # 대화 히스토리 추가
                    st.session_state.conversation_history.append({
                        "question": question,
                        "answer": answer
                    })
                    
                    # 답변 표시
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown("### 📋 답변")
                    st.write(answer)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 참고 약관 표시
                    try:
                        retriever = get_retriever()
                        docs = retriever.invoke(question)
                        
                        if docs:
                            st.markdown('<div class="source-box">', unsafe_allow_html=True)
                            st.markdown("### 📚 참고 약관")
                            
                            for i, doc in enumerate(docs[:2], 1):
                                with st.expander(
                                    f"📄 {doc.metadata.get('source', 'Unknown')} - 문서 {i}"
                                ):
                                    st.write(doc.page_content)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.warning(f"⚠️ 참고 약관 조회 실패: {str(e)}")
                
                except Exception as e:
                    st.error(f"❌ 오류 발생: {str(e)}")
    elif not st.session_state.qdrant_ready:
        st.markdown("""
<div class="warning-box">
<h3>⚠️ 시스템 준비 중</h3>
<p>Qdrant 서버를 실행한 후 페이지를 새로고침하세요 (F5)</p>
<p><b>터미널에서 다음을 실행하세요:</b></p>
<pre>docker run -p 6333:6333 qdrant/qdrant</pre>
</div>
""", unsafe_allow_html=True)

# 대화 히스토리 표시
with col2:
    st.subheader("📝 대화 히스토리")
    
    if st.session_state.conversation_history:
        for i, conv in enumerate(reversed(st.session_state.conversation_history), 1):
            with st.expander(f"질문 {len(st.session_state.conversation_history) - i + 1}"):
                st.markdown("**Q:** " + conv["question"])
                st.markdown("---")
                st.markdown("**A:** " + conv["answer"][:200] + "..." 
                          if len(conv["answer"]) > 200 else conv["answer"])
    else:
        st.info("아직 질문이 없습니다. 왼쪽에서 질문을 입력해보세요! 👈")

# 하단 정보
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; font-size: 0.85rem;">
    <p>🔐 <b>보안:</b> 모든 데이터는 로컬에서 처리되며, 외부로 전송되지 않습니다.</p>
    <p>⚡ <b>기술:</b> LangChain + Upstage Solar + Qdrant Vector DB</p>
    <p>📜 <b>버전:</b> v1.1.0 (Qdrant 연결 진단 개선) | 마지막 업데이트: 2026년 1월 15일</p>
</div>
""", unsafe_allow_html=True)
