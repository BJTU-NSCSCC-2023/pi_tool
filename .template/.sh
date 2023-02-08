test "$(cat ${NSCSCC2023_BJTU_PI_TOOL_HOME}/spear.txt)" = "nscscc2023_bjtu_pi_tool" || echo -e "\033[31mCannot find spear. Check if NSCSCC2023_BJTU_PI_TOOL_HOME set properly.\033[m" || exit 1
source ${NSCSCC2023_BJTU_PI_TOOL_HOME}/sh_lib/check_before_run.sh
