import logging
from pathlib import Path
import subprocess

from typing import override
from spike.domain.ports.scaffold_builder import ScaffoldBuilder
from spike.domain.value_objects.scaffold_payload import ScaffoldPayload

logger = logging.getLogger(__name__)

class AgentEngineScaffoldBuilder(ScaffoldBuilder):
    
    @override
    async def build(self,
        scaffold_payload: ScaffoldPayload,
    ) -> str:
        scaffold_type = scaffold_payload.type
        prompt = scaffold_payload.prompt
        context = scaffold_payload.context
        
        system_prompt_file = f"/Users/xxxx/Projects/pangu/contexts/spike/src/spike/infrastructure/adapters/prompts/scaffold/{scaffold_type}.md"
        if not Path(system_prompt_file).exists():
            raise NotImplementedError(f"{scaffold_type} not implemented")
            
        args = [
            "agent-engine",
            "execute-session",
            prompt,
            "--project", "pangu",
            "--context", context,
            "--system-prompt-file", system_prompt_file,
            "--context-payload", scaffold_payload.model_dump_json()
        ]
        try:
            result = subprocess.run(
                args=args,
                capture_output=True,  # 捕获 stdout 和 stderr
                text=True,            # 以字符串格式返回结果 (等同于 universal_newlines=True)
                check=True            # 如果命令返回非零退出状态码，自动抛出 CalledProcessError 异常
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"subprocess.CalledProcessError: {e}")
            raise e