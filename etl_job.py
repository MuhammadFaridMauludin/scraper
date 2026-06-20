from storage import list_objects, download_object, upload_processed, object_exists, mark_done
from db import transform_jobs, save_raw_to_db, save_clean_to_db


def main():
    print("🔄 ETL Job — memproses file dari Object Storage /raw")

    raw_files = list_objects("raw/")
    raw_files = [f for f in raw_files if f.endswith(".json")]

    to_process = []
    for f in raw_files:
        flag = f.replace(".json", ".done")
        if not object_exists(flag):
            to_process.append(f)

    if not to_process:
        print("Tidak ada file baru. Selesai.")
        return

    print(f"Ditemukan {len(to_process)} file baru")

    for object_name in to_process:
        print(f"\n  📄 Memproses: {object_name}")
        try:
            jobs_raw = download_object(object_name)
            if not jobs_raw:
                print(f"    ⚠️ Gagal download atau file kosong")
                continue

            jobs_clean = transform_jobs(jobs_raw)

            processed_name = object_name.replace("raw/", "processed/")
            status = upload_processed(jobs_clean, processed_name)
            print(f"    ☁️  Processed → {processed_name} (status {status})")

            save_raw_to_db(jobs_raw)
            save_clean_to_db(jobs_clean)
            print(f"    💾 {len(jobs_clean)} job disimpan ke Autonomous DB")

            mark_done(object_name)
            print(f"    ✅ Selesai")

        except Exception as e:
            print(f"    ❌ Error: {e}")
            continue

    print("\n🎉 ETL selesai!")


if __name__ == "__main__":
    main()