import { PageCursor } from '@/types/page-cursor.types'
import {
    InfiniteData,
    QueryKey,
    useInfiniteQuery,
    UseInfiniteQueryOptions,
    UseInfiniteQueryResult,
    useMutation,
    UseMutationResult,
    useQuery,
    UseQueryOptions,
    UseQueryResult,
} from '@tanstack/react-query'
import { apiClient } from './api-client'

export type QueryOptions<T = unknown> = Omit<
    UseQueryOptions<T>,
    'queryKey' | 'queryFn'
>
export type InfiniteQueryOptions<T = unknown> = Omit<
    UseInfiniteQueryOptions<T, Error, InfiniteData<T>, QueryKey, string>,
    'queryKey' | 'queryFn' | 'initialPageParam' | 'getNextPageParam'
>

export interface PropsOptionsQuery {
    options?: QueryOptions
}

export type MutationProps<DataT = unknown, VarT = unknown> = {
    onSuccess?: (data: DataT, variables: VarT) => void
    onError?: (error: any, variables: VarT) => void
}

interface PageParams {
    cursor?: string
    per_page?: number
}

export interface ApiHelperProps<TParams = object> extends PropsOptionsQuery {
    params?: TParams & PageParams
    signal?: AbortSignal
}

export interface MutationApiHelperProps<
    TData = unknown,
    TParams = object,
> extends ApiHelperProps<TParams> {
    data?: TData
}

export function useApiHelper<T, TGetProps extends ApiHelperProps>({
    url,
    queryKey,
    getFn,
    formatParams,
}: {
    url: (props: TGetProps) => string
    queryKey: (props: TGetProps) => QueryKey
    getFn?: (props: TGetProps & { signal?: AbortSignal }) => Promise<T>
    formatParams?: (props: TGetProps) => QueryParams
}): {
    get: (props: TGetProps) => Promise<T>
    useGet: (
        props?: Omit<TGetProps, 'options'> & { options?: QueryOptions<T> },
    ) => UseQueryResult<T>
    queryKey: (props: TGetProps) => QueryKey
} {
    const get = async (props: TGetProps) => {
        if (getFn) return getFn(props)
        return apiClient
            .get(url(props), {
                searchParams: toSearchParams(
                    formatParams ? formatParams(props) : (props.params as QueryParams),
                ),
                signal: props.signal,
            })
            .json<T>()
    }
    const useGet = (
        props?: Omit<TGetProps, 'options'> & { options?: QueryOptions<T> },
    ) => {
        return useQuery<T>({
            queryKey: queryKey((props || {}) as TGetProps),
            queryFn: ({ signal }) =>
                get({ ...((props || {}) as TGetProps), signal }),
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            ...(props?.options as any),
        }) as UseQueryResult<T>
    }
    return {
        get,
        useGet,
        queryKey,
    }
}

export function usePageApiHelper<
    T,
    TGetListProps extends ApiHelperProps,
    TListLookupData = unknown,
>({
    url,
    queryKey,
    getPageFn,
    formatParams,
}: {
    url: (props: TGetListProps) => string
    queryKey: (props: TGetListProps) => QueryKey
    getPageFn?: (
        props: TGetListProps & { signal?: AbortSignal },
    ) => Promise<PageCursor<T, TListLookupData>>
    formatParams?: (props: TGetListProps) => QueryParams
}): {
    getPage: (
        props: TGetListProps & { signal?: AbortSignal },
    ) => Promise<PageCursor<T, TListLookupData>>
    useGetPage: (
        props: Omit<TGetListProps, 'options'> & {
            options?: InfiniteQueryOptions<PageCursor<T, TListLookupData>>
        },
    ) => UseInfiniteQueryResult<
        InfiniteData<PageCursor<T, TListLookupData>, unknown>,
        Error
    >
    queryKey: (props: TGetListProps) => QueryKey
} {
    const getList = async (props: TGetListProps & { signal?: AbortSignal }) => {
        if (getPageFn) return getPageFn(props)
        return apiClient
            .get(url(props), {
                searchParams: toSearchParams({
                    cursor: props.params?.cursor,
                    per_page: props.params?.per_page,
                    ...(formatParams ? formatParams(props) : props.params),
                }),
                signal: props.signal,
            })
            .json<PageCursor<T, TListLookupData>>()
    }
    const useGetList = (
        props: Omit<TGetListProps, 'options'> & {
            options?: InfiniteQueryOptions<PageCursor<T, TListLookupData>>
        },
    ) => {
        return useInfiniteQuery({
            queryKey: queryKey({
                ...props,
                params: props?.params,
            } as TGetListProps),
            queryFn: ({ pageParam, signal }) =>
                getList({
                    ...props,
                    signal,
                    params: {
                        ...props.params,
                        cursor: pageParam,
                    },
                } as TGetListProps),
            initialPageParam: '',
            getNextPageParam: (lastPage) => lastPage.cursor,
            ...(props.options as any),
        })
    }
    return {
        getPage: getList,
        useGetPage: useGetList,
        queryKey,
    }
}

export function useMutationApiHelper<
    T,
    TMutateProps extends MutationApiHelperProps,
>({
    url,
    method,
    fetchFn,
    onSuccess,
    formatParams,
}: {
    url: (props: TMutateProps) => string
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
    fetchFn?: (props: TMutateProps) => Promise<T>
    onSuccess?: ({
        data,
        variables,
    }: {
        data: T
        variables: TMutateProps
    }) => void
    formatParams?: (props: TMutateProps) => QueryParams
}): {
    mutation: (props: TMutateProps) => Promise<T>
    useMutation: (
        props: MutationProps<T, TMutateProps>,
    ) => UseMutationResult<T, any, TMutateProps>
} {
    const fn = async (props: TMutateProps) => {
        if (fetchFn) return fetchFn(props)
        const response = await apiClient(url(props), {
            method: method.toLowerCase(),
            json: props.data,
            searchParams: toSearchParams(
                formatParams ? formatParams(props) : (props.params as QueryParams),
            ),
            signal: props.signal,
        })
        const data = response.status === 204 ? (null as T) : await response.json<T>()
        onSuccess?.({ data, variables: props })
        return data
    }
    const useMut = (
        props: MutationProps<T, TMutateProps> = {},
    ): UseMutationResult<T, any, TMutateProps> => {
        return useMutation({
            mutationFn: fn,
            ...props,
        })
    }
    return {
        mutation: fn,
        useMutation: useMut,
    }
}

export async function fetchAllPages<
    T,
    TGetListProps extends ApiHelperProps,
    TListLookupData = unknown,
>(
    getList: (props: TGetListProps) => Promise<PageCursor<T, TListLookupData>>,
    props: TGetListProps,
): Promise<T[]> {
    const all: T[] = []
    let cursor: string | undefined = props?.params?.cursor ?? ''

    while (cursor !== undefined) {
        const p = {
            ...props,
            params: {
                ...props.params,
                cursor,
            },
        } as TGetListProps

        const res = await getList(p)
        const items = res.items
        all.push(...items)

        cursor = (res as unknown as { cursor?: string }).cursor
        if (!cursor) break
    }

    return all
}

type QueryParams = Record<
    string,
    string | number | boolean | undefined | null | string[] | number[]
>

function toSearchParams(
    params?: QueryParams,
): (string | number | boolean)[][] | undefined {
    if (!params) return undefined
    const result: (string | number | boolean)[][] = []
    for (const [k, v] of Object.entries(params)) {
        if (v == null) continue
        if (Array.isArray(v)) {
            for (const item of v) result.push([k, item])
        } else {
            result.push([k, v])
        }
    }
    return result
}

export function pageItemsFlatten<T = Record<string, unknown>, L = unknown>(
    data: InfiniteData<PageCursor<T, L>> | undefined,
): T[] {
    if (!data) return []
    return data.pages.map((p) => p.items).flat()
}
