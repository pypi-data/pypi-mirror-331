file(REMOVE_RECURSE
  "libnexa-qwen2-audio-lib_shared.pdb"
  "libnexa-qwen2-audio-lib_shared.so"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/nexa-qwen2-audio-lib_shared.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
