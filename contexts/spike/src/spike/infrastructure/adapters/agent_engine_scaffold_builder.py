import logging
import subprocess

from typing import override
from spike.domain.enums.context_name import ContextName
from spike.domain.enums.scaffold_type import ScaffoldType
from spike.domain.ports.scaffold_builder import ScaffoldBuilder

logger = logging.getLogger(__name__)

class AgentEngineScaffoldBuilder(ScaffoldBuilder):
    
    @override
    async def build(self,
        scaffold_type: ScaffoldType,
        context: ContextName,
        description: str,
    ) -> str:
        system_prompt_file = f"/Users/xxxx/Projects/pangu/contexts/spike/src/spike/infrastructure/adapters/prompts/scaffold/{scaffold_type}.md"
        args = [
            "agent-engine",
            "execute-session",
            description,
            "--project", "pangu",
            "--context", context,
            # "--system-prompt-file", system_prompt_file
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