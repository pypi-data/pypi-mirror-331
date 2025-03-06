file(REMOVE_RECURSE
  "libomni_audio_static.a"
  "libomni_audio_static.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/omni_audio_static.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
