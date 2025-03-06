file(REMOVE_RECURSE
  "libomni_audio_shared.pdb"
  "libomni_audio_shared.so"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/omni_audio_shared.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
