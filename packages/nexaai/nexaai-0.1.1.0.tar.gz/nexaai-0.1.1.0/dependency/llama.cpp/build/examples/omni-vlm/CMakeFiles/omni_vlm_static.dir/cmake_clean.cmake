file(REMOVE_RECURSE
  "libomni_vlm_static.a"
  "libomni_vlm_static.pdb"
)

# Per-language clean rules from dependency scanning.
foreach(lang CXX)
  include(CMakeFiles/omni_vlm_static.dir/cmake_clean_${lang}.cmake OPTIONAL)
endforeach()
