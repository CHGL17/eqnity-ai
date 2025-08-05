import uuid
import time
from agent.main import agent_executor, update_agent_language
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from utils import format_tool_call
from i18n.utils import i18n, t

session_threads = {}

def get_or_create_thread_id(session_id):
    if session_id not in session_threads:
        session_threads[session_id] = str(uuid.uuid4())
    return session_threads[session_id]

def chat_function(message, history, session_id):
    try:
        thread_id = get_or_create_thread_id(session_id)
        config = RunnableConfig(configurable={"thread_id": thread_id}, run_id=uuid.uuid4())
        thinking_message = {
            "role": "assistant",
            "content": f"""
<div class="thinking-box">
    <div class="thinking-title">{t('processing_request')}</div>
    <div class="thinking-content"></div>
</div>
            """
        }
        history.append(thinking_message)
        yield history

        input_message = HumanMessage(content=message)
        accumulated_thoughts = ""
        final_response_content = ""
        tool_calls_count = 0

        for event in agent_executor.stream(
            {"messages": [input_message]},
            config,
            stream_mode="values"
        ):
            if "messages" not in event:
                continue
            for msg in event["messages"]:
                new_thought = ""
                if hasattr(msg, 'type') and msg.type == "ai" and hasattr(msg, "tool_calls") and msg.tool_calls:
                    tool_calls_count += 1
                    for tool_call in msg.tool_calls:
                        tool_info = format_tool_call(tool_call)
                        new_thought += f"\n\n**{t('tool_call')} #{tool_calls_count}**\n{tool_info}"
                        time.sleep(0.3)
                elif hasattr(msg, 'type') and msg.type == "tool":
                    result_preview = str(msg.content)[:150] + "..." if len(str(msg.content)) > 150 else str(msg.content)
                    new_thought += f"\n\n**{t('tool_result')}**\n`{result_preview}`"
                    time.sleep(0.2)
                elif hasattr(msg, 'type') and msg.type == "ai" and hasattr(msg, 'content') and msg.content:
                    if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                        final_response_content = msg.content
                if new_thought:
                    accumulated_thoughts += new_thought
                    thinking_content = accumulated_thoughts.strip()
                    history[-1]["content"] = f"""
<div class="thinking-box">
    <div class="thinking-title">{t('processing_request')}</div>
    <div class="thinking-content">{thinking_content}</div>
</div>
                    """
                    yield history

        final_thinking_content = accumulated_thoughts.strip()
        history[-1]["content"] = f"""
<div class="thinking-box done">
    <div class="thinking-title">{t('analysis_completed')}</div>
    <div class="thinking-content">{final_thinking_content}</div>
</div>
        """
        yield history

        if final_response_content:
            time.sleep(0.5)
            history.append({
                "role": "assistant",
                "content": final_response_content
            })
            yield history

    except Exception as e:
        error_message = f"{t('error_occurred')}: {str(e)}"
        history.append({"role": "assistant", "content": error_message})
        yield history

def clear_conversation(session_id):
    if session_id in session_threads:
        del session_threads[session_id]
    return [{
        "role": "assistant",
        "content": t('conversation_restarted')
    }]

def update_language(lang: str):
    """Actualiza el idioma del sistema"""
    i18n.set_language(lang)
    update_agent_language(lang)